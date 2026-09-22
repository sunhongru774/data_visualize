<template>

  <div class="dashboard">

    <!-- 顶部 -->
    <header class="header">

      <div class="title">
        中国肺结核疫情数据可视化
      </div>

      <div class="subtitle">
        全国肺结核发病特征与时空分布分析
      </div>

    </header>


    <!-- 主体 -->
    <main class="main">


      <!-- 左侧 -->
      <section class="left-panel">


        <!-- 职业 -->
        <div class="panel career-panel">

          <div class="panel-title">
            肺结核患者职业分布
          </div>

          <img
            src="/charts/career.svg"
            class="chart-image"
            alt="肺结核患者职业分布"
          />

        </div>


        <!-- 全国趋势 -->
        <div class="panel trend-panel">

          <div class="panel-title">
            全国肺结核发病趋势
          </div>

          <img
            src="/charts/trend.svg"
            class="chart-image"
            alt="全国肺结核发病趋势"
          />

        </div>


      </section>



      <!-- 中央地图 -->
      <section class="center-panel">

        <div class="map-title">
          全国肺结核地区发病率
        </div>

        <div class="map-container">

          <LungMap />

        </div>

      </section>



      <!-- 右侧 -->
      <section class="right-panel">


        <!-- 年龄 -->
        <div class="panel age-panel">

          <div class="panel-title">
            不同年龄组肺结核发病特征
          </div>

          <img
            src="/charts/age_bar.svg"
            class="chart-image"
            alt="不同年龄组肺结核发病特征"
          />

        </div>


        <!-- TOP10 -->
        <div class="panel province-panel">

          <div class="panel-title">
            各地区肺结核发病率 TOP10
          </div>

          <img
            src="/charts/province_top10.svg"
            class="chart-image"
            alt="各地区肺结核发病率排名"
          />

        </div>


      </section>

    </main>

  </div>

</template>


<script setup>

import LungMap from './components/LungMap.vue'

</script>


<style scoped>

.dashboard {

  width: 100vw;
  height: 100vh;

  overflow: hidden;

  background:
    radial-gradient(
      circle at center,
      #082b43 0%,
      #031521 55%,
      #020b12 100%
    );

  color: #d9f7ff;

  font-family:
    "Microsoft YaHei",
    Arial,
    sans-serif;

}


/* =========================
   顶部
========================= */

.header {

  height: 13%;

  display: flex;

  flex-direction: column;

  justify-content: center;

  align-items: center;

}


.title {

  font-size: 32px;

  font-weight: bold;

  letter-spacing: 6px;

  color: #e8fbff;

}


.subtitle {

  margin-top: 8px;

  font-size: 14px;

  letter-spacing: 3px;

  color: #65cfe9;

}


/* =========================
   主体
========================= */

.main {

  height: 87%;

  display: grid;

  grid-template-columns:
    27% 46% 27%;

  gap: 10px;

  padding: 10px 20px 20px;

  box-sizing: border-box;

}


/* =========================
   左右区域
========================= */

.left-panel,
.right-panel {

  display: grid;

  grid-template-rows:
    1fr 1fr;

  gap: 10px;

}


/* =========================
   中央
========================= */

.center-panel {

  position: relative;

  border:
    1px solid rgba(
      48,
      190,
      230,
      0.35
    );

  background:
    rgba(
      3,
      30,
      47,
      0.35
    );

}


.map-title {

  position: absolute;

  top: 15px;

  left: 20px;

  z-index: 10;

  font-size: 18px;

  font-weight: bold;

  color: #8deaff;

}


.map-container {

  width: 100%;

  height: 100%;

}


/* =========================
   图表面板
========================= */

.panel {

  position: relative;

  border:
    1px solid rgba(
      48,
      190,
      230,
      0.30
    );

  background:
    rgba(
      4,
      34,
      52,
      0.45
    );

  overflow: hidden;

}


.panel-title {

  position: absolute;

  left: 15px;

  top: 12px;

  z-index: 5;

  font-size: 15px;

  font-weight: bold;

  color: #82e8ff;

}


.chart-image {

  width: 100%;

  height: 100%;

  object-fit: contain;

  padding: 25px 10px 5px;

  box-sizing: border-box;

}


/* =========================
   屏幕适配
========================= */

@media (max-width: 1200px) {

  .title {
    font-size: 25px;
  }

  .main {
    grid-template-columns:
      28% 44% 28%;
  }

}

</style>