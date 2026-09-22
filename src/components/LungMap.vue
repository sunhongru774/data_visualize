<template>
  <div ref="mapRef" class="lung-map"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import chinaJson from '../data/zone.json'

const mapRef = ref(null)

let chart = null

onMounted(() => {
  chart = echarts.init(mapRef.value)

  // 注册中国地图
  echarts.registerMap('china', chinaJson)

  // 从 zone.json 中读取数据
  const mapData = chinaJson.features.map(item => {
    const name = item.properties.name

    return {
      name: name,
      value: item.properties.value ?? 0,
      cases: item.properties.cases ?? 0,
      deaths: item.properties.deaths ?? 0
    }
  })

  const option = {
    backgroundColor: 'transparent',

    tooltip: {
      trigger: 'item',

      formatter(params) {
        const data = params.data || {}

        return `
          <div style="font-size:14px">
            <div style="font-size:16px;font-weight:bold;margin-bottom:8px">
              ${params.name}
            </div>

            <div>发病数：${formatNumber(data.cases || 0)} 例</div>
            <div>发病率：${Number(data.value || 0).toFixed(2)} /10万</div>
            <div>死亡数：${formatNumber(data.deaths || 0)} 例</div>
          </div>
        `
      }
    },

    visualMap: {
      min: 0,
      max: 150,

      left: 'center',
      bottom: 20,

      text: [
        '高发病率',
        '低发病率'
      ],

      calculable: true,

      textStyle: {
        color: '#d9f7ff'
      },

      inRange: {
        color: [
          '#0b2a42',
          '#075985',
          '#0284c7',
          '#22d3ee',
          '#facc15',
          '#ef4444'
        ]
      }
    },

    series: [
      {
        name: '肺结核发病率',

        type: 'map',

        map: 'china',

        roam: true,

        zoom: 1.15,

        selectedMode: false,

        label: {
          show: true,
          color: '#d8f3ff',
          fontSize: 10
        },

        emphasis: {
          label: {
            color: '#ffffff',
            fontSize: 12
          },

          itemStyle: {
            borderColor: '#ffffff',
            borderWidth: 1.5
          }
        },

        itemStyle: {
          borderColor: '#3cc9e8',
          borderWidth: 0.8,
          areaColor: '#082b43'
        },

        data: mapData
      }
    ]
  }

  chart.setOption(option)

  window.addEventListener('resize', resize)
})

function resize() {
  chart?.resize()
}

function formatNumber(num) {
  return Number(num || 0).toLocaleString('zh-CN')
}

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)

  if (chart) {
    chart.dispose()
  }
})
</script>

<style scoped>
.lung-map {
  width: 100%;
  height: 100%;
  min-height: 500px;
}
</style>