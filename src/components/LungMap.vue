<template>
  <div ref="mapRef" class="lung-map"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

const mapRef = ref(null)
let chart = null

// 简称 → GeoJSON 标准名 映射
const NAME_MAP = {
  '内蒙古自治区': '内蒙古',
  '广西壮族自治区': '广西',
  '西藏自治区': '西藏',
  '宁夏回族自治区': '宁夏',
  '新疆维吾尔自治区': '新疆',
  '北京市': '北京',
  '天津市': '天津',
  '上海市': '上海',
  '重庆市': '重庆'
}

onMounted(async () => {
  if (!mapRef.value) return
  chart = echarts.init(mapRef.value)

  try {
    // 并行拉取 GeoJSON 边界 + 业务数据
    const [geoRes, dataRes] = await Promise.all([
      fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json'),
      fetch('/data/zone_data.json')
    ])
    const geoJson = await geoRes.json()
    const zoneData = await dataRes.json()

    echarts.registerMap('china', geoJson)

    // 建立索引（支持全称和简称双向匹配）
    const dataIndex = {}
    zoneData.forEach(item => {
      dataIndex[item.name] = item
      for (const [full, short] of Object.entries(NAME_MAP)) {
        if (short === item.name) dataIndex[full] = item
      }
    })

    const mapData = geoJson.features.map(f => {
      const name = f.properties.name
      const matched = dataIndex[name] ||
        dataIndex[name.replace(/省|市|自治区|壮族|回族|维吾尔/g, '')]
      return {
        name,
        value: matched ? matched.incidence : 0,
        cases: matched ? matched.cases : 0,
        deaths: matched ? matched.deaths : 0,
        mortality: matched ? matched.mortality : 0
      }
    })

    chart.setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(3,25,45,0.95)',
        borderColor: 'rgba(80,220,250,0.5)',
        borderWidth: 1,
        textStyle: { color: '#eaffff' },
        formatter(params) {
          const d = params.data || {}
          return `
            <div style="min-width:150px;line-height:1.8;">
              <strong>${params.name}</strong><br>
              发病率：${Number(d.value || 0).toFixed(2)} /10万<br>
              发病例数：${Number(d.cases || 0).toLocaleString()} 例<br>
              死亡人数：${Number(d.deaths || 0).toLocaleString()} 例<br>
              死亡率：${Number(d.mortality || 0).toFixed(3)} /10万
            </div>
          `
        }
      },
      // ✅ 图例移到右下角，尺寸加大
      visualMap: {
        type: 'continuous',
        min: 0,
        max: 200,
        calculable: true,
        orient: 'vertical',
        right: 25,
        bottom: 30,
        itemWidth: 20,
        itemHeight: 150,
        text: ['高', '低'],
        textGap: 10,
        textStyle: { color: '#d8f8ff', fontSize: 12 },
        inRange: {
          color: ['#0b2a42', '#075985', '#0ea5e9', '#fbbf24', '#ef4444']
        }
      },
      geo: {
        map: 'china',
        roam: true,
        zoom: 1.15,
        center: [104, 35],
        selectedMode: false,
        label: { show: false },
        itemStyle: {
          borderColor: 'rgba(155,239,255,0.65)',
          borderWidth: 0.8,
          areaColor: '#164a62'
        },
        emphasis: {
          label: { show: true, color: '#fff', fontSize: 12 },
          itemStyle: {
            borderColor: '#fff',
            borderWidth: 1.5,
            areaColor: '#35bfc4'
          }
        }
      },
      series: [{
        name: '肺结核发病率',
        type: 'map',
        map: 'china',
        geoIndex: 0,
        data: mapData
      }]
    })

    window.addEventListener('resize', resize)
  } catch (err) {
    console.error('地图加载失败：', err)
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
.lung-map {
  width: 100%;
  height: 100%;
  min-height: 300px;
}
</style>