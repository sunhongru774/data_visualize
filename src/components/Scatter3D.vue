<template>
  <div ref="chartRef" class="scatter3d"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import 'echarts-gl'

const chartRef = ref(null)
let chart = null

// 全国各省人口规模（第七次全国人口普查，单位：百万人），key 用省级全称
const POPULATION_MILLION = {
  '北京市': 21.516, '天津市': 15.168, '河北省': 73.8375,
  '山西省': 36.4796, '内蒙古自治区': 25.0481, '辽宁省': 43.9100,
  '吉林省': 27.5238, '黑龙江省': 38.3300, '上海市': 24.2568,
  '江苏省': 79.6006, '浙江省': 55.0800, '安徽省': 60.8290,
  '福建省': 38.0600, '江西省': 45.4216, '山东省': 97.8943,
  '河南省': 94.3600, '湖北省': 58.1600, '湖南省': 67.3724,
  '广东省': 107.2400, '广西壮族自治区': 47.5400, '海南省': 9.0348,
  '重庆市': 29.9140, '四川省': 81.4020, '贵州省': 35.0803,
  '云南省': 47.1390, '西藏自治区': 3.1755, '陕西省': 37.7512,
  '甘肃省': 25.9078, '青海省': 5.8342, '宁夏回族自治区': 6.6154,
  '新疆维吾尔自治区': 22.9847,
}

// 解 3×3 线性方程组 Mx = b，用克拉默法则
function solve3(M, b) {
  const det = M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
            - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
            + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0])
  if (Math.abs(det) < 1e-12) return [0, 0, 0]
  const M1 = [[b[0], M[0][1], M[0][2]], [b[1], M[1][1], M[1][2]], [b[2], M[2][1], M[2][2]]]
  const M2 = [[M[0][0], b[0], M[0][2]], [M[1][0], b[1], M[1][2]], [M[2][0], b[2], M[2][2]]]
  const M3 = [[M[0][0], M[0][1], b[0]], [M[1][0], M[1][1], b[1]], [M[2][0], M[2][1], b[2]]]
  const det1 = M1[0][0] * (M1[1][1] * M1[2][2] - M1[1][2] * M1[2][1])
             - M1[0][1] * (M1[1][0] * M1[2][2] - M1[1][2] * M1[2][0])
             + M1[0][2] * (M1[1][0] * M1[2][1] - M1[1][1] * M1[2][0])
  const det2 = M2[0][0] * (M2[1][1] * M2[2][2] - M2[1][2] * M2[2][1])
             - M2[0][1] * (M2[1][0] * M2[2][2] - M2[1][2] * M2[2][0])
             + M2[0][2] * (M2[1][0] * M2[2][1] - M2[1][1] * M2[2][0])
  const det3 = M3[0][0] * (M3[1][1] * M3[2][2] - M3[1][2] * M3[2][1])
             - M3[0][1] * (M3[1][0] * M3[2][2] - M3[1][2] * M3[2][0])
             + M3[0][2] * (M3[1][0] * M3[2][1] - M3[1][1] * M3[2][0])
  return [det1 / det, det2 / det, det3 / det]
}

onMounted(async () => {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value)

  try {
    const res = await fetch('/data/zone_data.json')
    const zoneData = await res.json()

    // 组装三维散点数据：X=人口(百万), Y=发病率, Z=死亡率
    const points = []
    zoneData.forEach(item => {
      const pop = POPULATION_MILLION[item.name]
      if (pop && item.incidence != null && item.mortality != null) {
        points.push({
          name: item.name,
          value: [pop, Number(item.incidence), Number(item.mortality)]
        })
      }
    })

    if (points.length < 3) {
      console.warn('三维图：有效省份不足 3 个')
      return
    }

    // 最小二乘拟合 z = a + b·x + c·y
    const n = points.length
    let sx = 0, sy = 0, sz = 0
    let sxx = 0, syy = 0, sxy = 0, sxz = 0, syz = 0
    points.forEach(p => {
      const [x, y, z] = p.value
      sx += x; sy += y; sz += z
      sxx += x * x; syy += y * y; sxy += x * y
      sxz += x * z; syz += y * z
    })
    const [a, b, c] = solve3(
      [[n, sx, sy], [sx, sxx, sxy], [sy, sxy, syy]],
      [sz, sxz, syz]
    )

    // 计算 R²
    let ssRes = 0, ssTot = 0
    const zMean = sz / n
    points.forEach(p => {
      const [x, y, z] = p.value
      const pred = a + b * x + c * y
      ssRes += (z - pred) ** 2
      ssTot += (z - zMean) ** 2
    })
    const r2 = ssTot > 1e-12 ? 1 - ssRes / ssTot : 0

    // 生成回归平面网格
    const xMin = Math.min(...points.map(p => p.value[0]))
    const xMax = Math.max(...points.map(p => p.value[0]))
    const yMin = Math.min(...points.map(p => p.value[1]))
    const yMax = Math.max(...points.map(p => p.value[1]))
    const STEP = 20
    const surfaceData = []
    for (let i = 0; i <= STEP; i++) {
      for (let j = 0; j <= STEP; j++) {
        const x = xMin + (xMax - xMin) * i / STEP
        const y = yMin + (yMax - yMin) * j / STEP
        surfaceData.push([x, y, a + b * x + c * y])
      }
    }

    // 发病率范围用于 visualMap
    const incArr = points.map(p => p.value[1])
    const incMin = Math.min(...incArr)
    const incMax = Math.max(...incArr)

    chart.setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(3,25,45,0.95)',
        borderColor: 'rgba(80,220,250,0.5)',
        textStyle: { color: '#eaffff' },
        formatter(params) {
          if (params.seriesType === 'scatter3D') {
            const [x, y, z] = params.value
            return `<div style="min-width:150px;line-height:1.7">
              <strong>${params.data.name}</strong><br>
              人口规模：${x.toFixed(1)} 百万<br>
              发病率：${y.toFixed(2)} /10万<br>
              死亡率：${z.toFixed(3)} /10万
            </div>`
          }
          return ''
        }
      },
      visualMap: {
        show: true,
        dimension: 1,
        min: incMin,
        max: incMax,
        left: 20,
        bottom: 20,
        text: ['高', '低'],
        calculable: true,
        itemWidth: 14,
        itemHeight: 100,
        textStyle: { color: '#d9f7ff', fontSize: 11 },
        inRange: { color: ['#31d6ff', '#facc15', '#ef4444'] }
      },
      xAxis3D: {
        type: 'value',
        name: '人口(百万)',
        nameTextStyle: { color: '#ffffff', fontSize: 11 },
        axisLabel: { color: '#ffffff', fontSize: 9 },
        axisLine: { lineStyle: { color: '#2f5a73' } },
        splitLine: { lineStyle: { color: '#2f5a73', opacity: 0.35 } }
      },
      yAxis3D: {
        type: 'value',
        name: '发病率',
        nameTextStyle: { color: '#ffffff', fontSize: 11 },
        axisLabel: { color: '#ffffff', fontSize: 9 },
        axisLine: { lineStyle: { color: '#2f5a73' } },
        splitLine: { lineStyle: { color: '#2f5a73', opacity: 0.35 } }
      },
      zAxis3D: {
        type: 'value',
        name: '死亡率',
        nameTextStyle: { color: '#ffffff', fontSize: 11 },
        axisLabel: { color: '#ffffff', fontSize: 9 },
        axisLine: { lineStyle: { color: '#2f5a73' } },
        splitLine: { lineStyle: { color: '#2f5a73', opacity: 0.35 } }
      },
      grid3D: {
        boxWidth: 100,
        boxDepth: 80,
        boxHeight: 60,
        environment: 'transparent',
        viewControl: {
          alpha: 20,
          beta: 40,
          distance: 200,
          autoRotate: false,
          rotateSensitivity: 1,
          zoomSensitivity: 1
        },
        axisPointer: { show: false },
        light: {
          main: { intensity: 1.2, shadow: false, alpha: 40, beta: 30 },
          ambient: { intensity: 0.4 }
        }
      },
      series: [
        {
          type: 'scatter3D',
          name: '省份',
          data: points,
          symbolSize: 14,
          itemStyle: {
            borderColor: '#061824',
            borderWidth: 0.5,
            opacity: 0.95
          },
          label: {
            show: false
          },
          emphasis: {
            label: {
              show: true,
              color: '#ffffff',
              fontSize: 12,
              formatter: p => p.data.name
            }
          }
        },
        {
          type: 'surface',
          name: '回归平面',
          data: surfaceData,
          shading: 'lambert',
          wireframe: { show: false },
          itemStyle: { color: '#31d6ff', opacity: 0.28 },
          silent: true
        }
      ],
      graphic: [{
        type: 'text',
        left: 18,
        top: 18,
        style: {
          text: `R² = ${r2.toFixed(3)}\nZ = ${a.toFixed(3)} + ${b.toFixed(5)}·X + ${c.toFixed(5)}·Y\nn = ${n}`,
          fill: '#ffffff',
          fontSize: 11,
          lineHeight: 16,
          padding: [8, 12],
          backgroundColor: 'rgba(11,42,66,0.88)',
          borderColor: '#31d6ff',
          borderWidth: 1,
          borderRadius: 6
        }
      }]
    })

    window.addEventListener('resize', resize)
  } catch (err) {
    console.error('三维图加载失败：', err)
  }
})

function resize() {
  if (chart) chart.resize()
}

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  if (chart) {
    chart.dispose()
    chart = null
  }
})
</script>

<style scoped>
.scatter3d {
  width: 100%;
  height: 100%;
  min-height: 260px;
}
</style>