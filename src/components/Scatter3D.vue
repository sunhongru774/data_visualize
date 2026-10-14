<template>
  <div ref="chartRef" class="scatter3d"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'
import 'echarts-gl'
import { currentYear } from '../data/yearBus.js'

const chartRef = ref(null)
let chart = null

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

const NAME_TO_FULL = {
  '北京': '北京市', '天津': '天津市', '上海': '上海市', '重庆': '重庆市',
  '内蒙古': '内蒙古自治区', '广西': '广西壮族自治区',
  '西藏': '西藏自治区', '宁夏': '宁夏回族自治区',
  '新疆': '新疆维吾尔自治区',
}

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

/* 根据图表当前宽高，计算缩放系数（以 320x220 为基准 1.0） */
function getScaleFactor() {
  if (!chartRef.value) return 1
  const w = chartRef.value.clientWidth
  const h = chartRef.value.clientHeight
  if (!w || !h) return 1
  const k = Math.sqrt((w * h) / (320 * 220))
  return Math.max(0.9, Math.min(k, 2.4))
}

/* 应用随容器缩放的所有样式 */
function applyResponsiveStyle() {
  if (!chart) return
  const k = getScaleFactor()

  chart.setOption({
    visualMap: {
      itemWidth:  Math.round(10 * k),
      itemHeight: Math.round(70 * k),
      textStyle:  { color: '#ffffff', fontSize: Math.round(10 * k) }
    },
    xAxis3D: {
      nameTextStyle: { color: '#ffffff', fontSize: Math.round(10 * k) },
      axisLabel:     { color: '#ffffff', fontSize: Math.round(9  * k) }
    },
    yAxis3D: {
      nameTextStyle: { color: '#ffffff', fontSize: Math.round(10 * k) },
      axisLabel:     { color: '#ffffff', fontSize: Math.round(9  * k) }
    },
    zAxis3D: {
      nameTextStyle: { color: '#ffffff', fontSize: Math.round(10 * k) },
      axisLabel:     { color: '#ffffff', fontSize: Math.round(9  * k) }
    },
    series: [
      { type: 'scatter3D', symbolSize: Math.round(11 * k) },
      { type: 'surface' }
    ],
    graphic: [{
      id: 'statsBox',
      type: 'text',
      right:  Math.round(10 * k),
      bottom: Math.round(10 * k),
      style: {
        text: chart.__statsText || '',
        fill: '#a8e8ff',
        fontSize: Math.round(10 * k),
        lineHeight: Math.round(15 * k),
        fontWeight: 'bold',
        textAlign: 'left',
        padding: [Math.round(6 * k), Math.round(8 * k)],
        backgroundColor: 'rgba(11,42,66,0.85)',
        borderColor: '#31d6ff',
        borderWidth: 1,
        borderRadius: 4
      }
    }]
  })
}

async function render(year) {
  if (!chart) return
  try {
    const res = await fetch(`/data/zone_${year}.json`)
    const geoJson = await res.json()

    const points = []
    geoJson.features.forEach(f => {
      const p = f.properties || {}
      const shortName = p.name
      const fullName = NAME_TO_FULL[shortName] || shortName
      const pop = POPULATION_MILLION[fullName]
      const inc = p.incidence
      const mor = p.mortality
      if (pop && inc != null && mor != null) {
        points.push({
          name: shortName,
          value: [pop, Number(inc), Number(mor)]
        })
      }
    })

    if (points.length < 3) {
      console.warn(`三维图：${year} 年有效省份 < 3`)
      return
    }

    const n = points.length
    let sx = 0, sy = 0, sz = 0
    let sxx = 0, syy = 0, sxy = 0, sxz = 0, syz = 0
    points.forEach(pt => {
      const [x, y, z] = pt.value
      sx += x; sy += y; sz += z
      sxx += x * x; syy += y * y; sxy += x * y
      sxz += x * z; syz += y * z
    })
    const [a, b, c] = solve3(
      [[n, sx, sy], [sx, sxx, sxy], [sy, sxy, syy]],
      [sz, sxz, syz]
    )

    let ssRes = 0, ssTot = 0
    const zMean = sz / n
    points.forEach(pt => {
      const [x, y, z] = pt.value
      const pred = a + b * x + c * y
      ssRes += (z - pred) ** 2
      ssTot += (z - zMean) ** 2
    })
    const r2 = ssTot > 1e-12 ? 1 - ssRes / ssTot : 0

    /* ★ 把统计文字存到 chart 对象上，供 applyResponsiveStyle 使用 */
    chart.__statsText =
      `R² = ${r2.toFixed(3)}\n` +
      `Z = ${a.toFixed(4)} + ${b.toFixed(5)}·X + ${c.toFixed(5)}·Y\n` +
      `n = ${n}`

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

    const incArr = points.map(p => p.value[1])
    const incMin = Math.min(...incArr)
    const incMax = Math.max(...incArr)

    const k = getScaleFactor()

    chart.setOption({
      backgroundColor: 'transparent',

      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(3,25,45,0.95)',
        borderColor: 'rgba(80,220,250,0.5)',
        textStyle: { color: '#eaffff', fontSize: Math.round(12 * k) },
        formatter(params) {
          if (params.seriesType === 'scatter3D') {
            const [x, y, z] = params.value
            return `<div style="min-width:130px;line-height:1.6">
              <strong>${params.data.name}</strong><br>
              人口：${x.toFixed(1)} 百万<br>
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
        left: 6,
        bottom: 6,
        text: ['高', '低'],
        calculable: true,
        itemWidth:  Math.round(10 * k),
        itemHeight: Math.round(70 * k),
        textStyle:  { color: '#ffffff', fontSize: Math.round(10 * k) },
        inRange: { color: ['#31d6ff', '#facc15', '#ef4444'] }
      },

      xAxis3D: {
        type: 'value', name: '人口',
        nameTextStyle: { color: '#ffffff', fontSize: Math.round(10 * k) },
        axisLabel:     { color: '#ffffff', fontSize: Math.round(9  * k) },
        axisLine:  { lineStyle: { color: '#2f5a73' } },
        splitLine: { lineStyle: { color: '#2f5a73', opacity: 0.35 } }
      },
      yAxis3D: {
        type: 'value', name: '发病率',
        nameTextStyle: { color: '#ffffff', fontSize: Math.round(10 * k) },
        axisLabel:     { color: '#ffffff', fontSize: Math.round(9  * k) },
        axisLine:  { lineStyle: { color: '#2f5a73' } },
        splitLine: { lineStyle: { color: '#2f5a73', opacity: 0.35 } }
      },
      zAxis3D: {
        type: 'value', name: '死亡率',
        nameTextStyle: { color: '#ffffff', fontSize: Math.round(10 * k) },
        axisLabel:     { color: '#ffffff', fontSize: Math.round(9  * k) },
        axisLine:  { lineStyle: { color: '#2f5a73' } },
        splitLine: { lineStyle: { color: '#2f5a73', opacity: 0.35 } }
      },

      grid3D: {
        left: 0, right: 0, top: 10, bottom: 0,
        boxWidth: 160, boxDepth: 130, boxHeight: 100,
        environment: 'transparent',
        viewControl: {
          alpha: 22, beta: 35, distance: 130,
          autoRotate: false,
          rotateSensitivity: 1, zoomSensitivity: 1
        },
        axisPointer: { show: false },
        light: {
          main: { intensity: 1.2, shadow: false, alpha: 40, beta: 30 },
          ambient: { intensity: 0.5 }
        }
      },

      series: [
        {
          type: 'scatter3D', name: '省份',
          data: points,
          symbolSize: Math.round(11 * k),
          itemStyle: {
            borderColor: '#061824', borderWidth: 0.5, opacity: 0.95
          },
          label: { show: false },
          emphasis: {
            label: {
              show: true, color: '#ffffff',
              fontSize: Math.round(11 * k),
              formatter: p => p.data.name
            }
          }
        },
        {
          type: 'surface', name: '回归平面',
          data: surfaceData,
          shading: 'lambert',
          wireframe: { show: false },
          itemStyle: { color: '#31d6ff', opacity: 0.25 },
          silent: true
        }
      ],

      graphic: [{
        id: 'statsBox',
        type: 'text',
        right:  Math.round(10 * k),
        bottom: Math.round(10 * k),
        style: {
          text: chart.__statsText,
          fill: '#a8e8ff',
          fontSize: Math.round(10 * k),
          lineHeight: Math.round(15 * k),
          fontWeight: 'bold',
          textAlign: 'left',
          padding: [Math.round(6 * k), Math.round(8 * k)],
          backgroundColor: 'rgba(11,42,66,0.85)',
          borderColor: '#31d6ff',
          borderWidth: 1,
          borderRadius: 4
        }
      }]
    }, true)
  } catch (err) {
    console.error('三维图加载失败：', err)
  }
}

watch(currentYear, y => render(y))

onMounted(async () => {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value)
  await render(currentYear.value)
  window.addEventListener('resize', resize)
})

function resize() {
  if (chart) {
    chart.resize()
    applyResponsiveStyle()   // ★ 关键：resize 后重新根据尺寸应用样式
  }
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