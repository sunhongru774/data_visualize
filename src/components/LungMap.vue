<template>
  <div ref="mapRef" class="lung-map"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'
import { currentYear } from '../data/yearBus.js'

const mapRef = ref(null)
let chart = null
const geoCache = {}

const NAME_MAP = {
  '内蒙古自治区': '内蒙古', '广西壮族自治区': '广西',
  '西藏自治区': '西藏', '宁夏回族自治区': '宁夏',
  '新疆维吾尔自治区': '新疆',
  '北京市': '北京', '天津市': '天津',
  '上海市': '上海', '重庆市': '重庆'
}

async function loadGeo(y) {
  if (geoCache[y]) return geoCache[y]
  const r = await fetch(`/data/zone_${y}.json`)
  geoCache[y] = await r.json()
  return geoCache[y]
}

function buildData(geoJson) {
  return geoJson.features.map(f => {
    const p = f.properties || {}
    return {
      name: p.name,
      value: p.incidence || 0,
      cases: p.cases || 0,
      deaths: p.deaths || 0,
      mortality: p.mortality || 0,
      incidence: p.incidence || 0
    }
  })
}

function computeRange(data) {
  const arr = data.map(d => d.value).filter(v => v > 0)
  if (!arr.length) return [0, 1]
  const mx = Math.max(...arr)
  return [0, Math.max(1, Math.ceil(mx / 50) * 50)]
}

async function render(year) {
  if (!chart) return
  try {
    const geoJson = await loadGeo(year)
    echarts.registerMap('china_' + year, geoJson)
    const mapData = buildData(geoJson)
    const [vmin, vmax] = computeRange(mapData)

    chart.setOption({
      backgroundColor: 'transparent',
      title: {
        text: `${year} 年全国肺结核发病率分布`,
        left: 20, top: 8,
        textStyle: { color: '#dffaff', fontSize: 14, fontWeight: 600 }
      },
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
      visualMap: {
        type: 'continuous',
        min: vmin, max: vmax,
        calculable: true,
        orient: 'vertical',
        right: 25, bottom: 30,
        itemWidth: 20, itemHeight: 150,
        text: ['高', '低'], textGap: 10,
        textStyle: { color: '#d8f8ff', fontSize: 12 },
        inRange: {
          color: ['#0b2a42','#075985','#0ea5e9','#fbbf24','#ef4444']
        }
      },
      geo: {
        map: 'china_' + year,
        roam: true, zoom: 1.15, center: [104, 35],
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
            borderColor: '#fff', borderWidth: 1.5, areaColor: '#35bfc4'
          }
        }
      },
      series: [{
        name: '肺结核发病率',
        type: 'map',
        map: 'china_' + year,
        geoIndex: 0,
        data: mapData
      }]
    }, true)
  } catch (e) {
    console.error('地图加载失败：', e)
  }
}

watch(currentYear, y => render(y))

onMounted(async () => {
  if (!mapRef.value) return
  chart = echarts.init(mapRef.value)
  await render(currentYear.value)
  window.addEventListener('resize', resize)
})

function resize() { if (chart) chart.resize() }

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  if (chart) { chart.dispose(); chart = null }
})
</script>

<style scoped>
.lung-map { width: 100%; height: 100%; min-height: 300px; }
</style>