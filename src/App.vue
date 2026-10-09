<template>
  <div class="dashboard">

    <!-- ========================= -->
    <!-- 顶部标题 -->
    <!-- ========================= -->

    <header class="header">

      <div class="header-decoration left"></div>

      <div class="title-area">

        <h1>
          中国肺结核疫情数据可视化
        </h1>

        <p>
          NATIONAL PULMONARY TUBERCULOSIS
          EPIDEMIOLOGICAL VISUALIZATION
        </p>

      </div>

      <div class="header-decoration right"></div>

    </header>


    <!-- ========================= -->
    <!-- 主体 -->
    <!-- ========================= -->

    <main class="dashboard-main">

      <!-- ========================= -->
      <!-- 左侧 -->
      <!-- ========================= -->

      <section class="left-column">

        <!-- 职业 -->
        <div
          class="panel chart-panel clickable"
          @click="
            openChart(
              '/charts/career.svg',
              '肺结核患者职业构成分析'
            )
          "
        >

          <div class="panel-title">
            <span></span>
            肺结核患者职业构成
          </div>

          <div class="chart-image-wrapper">

            <img
              src="/charts/career.svg"
              alt="职业构成"
            />

          </div>

        </div>


        <!-- 全国趋势 -->
        <div
          class="panel chart-panel clickable"
          @click="
            openChart(
              '/charts/trend.svg',
              '全国肺结核疫情变化趋势'
            )
          "
        >

          <div class="panel-title">
            <span></span>
            全国肺结核疫情变化趋势
          </div>

          <div class="chart-image-wrapper">

            <img
              src="/charts/trend.svg"
              alt="全国趋势"
            />

          </div>

        </div>

      </section>


      <!-- ========================= -->
      <!-- 中央地图 -->
      <!-- ========================= -->

      <section class="center-column">

        <div class="map-panel panel">

          <div class="panel-title map-title">

            <span></span>

            全国肺结核发病率空间分布

            <button
              class="expand-button"
              @click.stop="
                openMap()
              "
            >
              ⛶
            </button>

          </div>

          <div class="map-container">

            <LungMap />

          </div>

        </div>

      </section>


      <!-- ========================= -->
      <!-- 右侧 -->
      <!-- ========================= -->

      <section class="right-column">

        <!-- 散点 -->
        <div
          class="panel chart-panel clickable"
          @click="
            openChart(
              '/charts/scatter_corr.svg',
              '发病率与死亡率相关性分析'
            )
          "
        >

          <div class="panel-title">

            <span></span>

            发病率与死亡率相关性分析

          </div>

          <div class="chart-image-wrapper">

            <img
              src="/charts/age_scatter.svg"
              alt="年龄散点分析"
            />

          </div>

        </div>


        <!-- 年龄 -->
        <div
          class="panel chart-panel clickable"
          @click="
            openChart(
              '/charts/age_bar.svg',
              '年龄组肺结核发病情况'
            )
          "
        >

          <div class="panel-title">

            <span></span>

            年龄组肺结核发病情况

          </div>

          <div class="chart-image-wrapper">

            <img
              src="/charts/age_bar.svg"
              alt="年龄组"
            />

          </div>

        </div>


        <!-- TOP10 -->
        <div
          class="panel chart-panel clickable"
          @click="
            openChart(
              '/charts/province_top10.svg',
              '各省肺结核发病率 TOP10'
            )
          "
        >

          <div class="panel-title">

            <span></span>

            各省肺结核发病率 TOP10

          </div>

          <div class="chart-image-wrapper">

            <img
              src="/charts/province_top10.svg"
              alt="省份TOP10"
            />

          </div>

        </div>

      </section>

    </main>


    <!-- ========================= -->
    <!-- 图表放大弹窗 -->
    <!-- ========================= -->

    <div
      v-if="modalVisible"
      class="modal"
      @click.self="closeModal"
    >

      <div class="modal-content">

        <div class="modal-header">

          <div class="modal-title">

            {{ modalTitle }}

          </div>

          <button
            class="close-button"
            @click="closeModal"
          >
            ×
          </button>

        </div>

        <div class="modal-body">

          <img
            v-if="modalType === 'chart'"
            :src="modalImage"
            :alt="modalTitle"
          />

          <div
            v-if="modalType === 'map'"
            class="modal-map"
          >

            <LungMap />

          </div>

        </div>

      </div>

    </div>


    <!-- ========================= -->
    <!-- 底部 -->
    <!-- ========================= -->

    <footer class="footer">

      数据来源：全国肺结核相关统计数据

      <span>
        ·
      </span>

      数据可视化分析系统

    </footer>

  </div>
</template>


<script setup>

import {
  ref
} from 'vue'

import LungMap from './components/LungMap.vue'


/* =========================
   弹窗
========================= */

const modalVisible = ref(false)

const modalImage = ref('')

const modalTitle = ref('')

const modalType = ref('chart')


/* =========================
   打开普通图表
========================= */

function openChart(
  image,
  title
) {

  modalImage.value = image

  modalTitle.value = title

  modalType.value = 'chart'

  modalVisible.value = true

}


/* =========================
   打开地图
========================= */

function openMap() {

  modalTitle.value =
    '全国肺结核发病率空间分布'

  modalType.value = 'map'

  modalVisible.value = true

}


/* =========================
   关闭
========================= */

function closeModal() {

  modalVisible.value = false

}

</script>


<style scoped>

/* =====================================================
   全局
===================================================== */

* {
  box-sizing: border-box;
}

.dashboard {

  width: 100vw;

  height: 100vh;

  overflow: hidden;

  color: #d9f7ff;

  background:
    radial-gradient(
      circle at 50% 40%,
      rgba(10, 76, 105, 0.28),
      transparent 45%
    ),
    linear-gradient(
      135deg,
      #020c19,
      #031927,
      #04121f
    );

  font-family:
    "Microsoft YaHei",
    "Noto Sans SC",
    Arial,
    sans-serif;

}


/* =====================================================
   顶部
===================================================== */

.header {

  height: 12%;

  min-height: 90px;

  position: relative;

  display: flex;

  justify-content: center;

  align-items: center;

}


.title-area {

  text-align: center;

}


.title-area h1 {

  margin: 0;

  font-size: clamp(
    28px,
    2.2vw,
    46px
  );

  letter-spacing: 5px;

  font-weight: 700;

  background:
    linear-gradient(
      90deg,
      #72e9ff,
      #ffffff,
      #65d6ff
    );

  -webkit-background-clip: text;

  -webkit-text-fill-color: transparent;

}


.title-area p {

  margin-top: 8px;

  font-size: 11px;

  letter-spacing: 5px;

  color: rgba(
    150,
    225,
    245,
    0.65
  );

}


.header-decoration {

  position: absolute;

  width: 20%;

  height: 1px;

  top: 70%;

  background:
    linear-gradient(
      90deg,
      transparent,
      rgba(
        50,
        211,
        245,
        0.8
      ),
      transparent
    );

}


.header-decoration.left {

  left: 5%;

}


.header-decoration.right {

  right: 5%;

}


/* =====================================================
   主体
===================================================== */

.dashboard-main {

  width: 96%;

  height: 83%;

  margin: 0 auto;

  display: grid;

  grid-template-columns:
    23%
    49%
    23%;

  gap: 2.5%;

}


/* =====================================================
   左右列
===================================================== */

.left-column,
.right-column {

  height: 100%;

  display: flex;

  flex-direction: column;

  gap: 2%;

}


/* =====================================================
   中央
===================================================== */

.center-column {

  height: 100%;

}


/* =====================================================
   面板
===================================================== */

.panel {

  position: relative;

  overflow: hidden;

  border:
    1px solid
    rgba(
      61,
      196,
      230,
      0.26
    );

  background:
    linear-gradient(
      135deg,
      rgba(
        5,
        31,
        50,
        0.88
      ),
      rgba(
        4,
        20,
        35,
        0.72
      )
    );

  box-shadow:
    inset 0 0 30px
    rgba(
      0,
      180,
      220,
      0.035
    ),
    0 0 20px
    rgba(
      0,
      100,
      140,
      0.08
    );

}


.panel::before {

  content: "";

  position: absolute;

  left: 0;

  top: 0;

  width: 40%;

  height: 1px;

  background:
    linear-gradient(
      90deg,
      #42ddff,
      transparent
    );

}


.panel::after {

  content: "";

  position: absolute;

  right: 0;

  bottom: 0;

  width: 40%;

  height: 1px;

  background:
    linear-gradient(
      90deg,
      transparent,
      #42ddff
    );

}


/* =====================================================
   图表面板
===================================================== */

.chart-panel {

  flex: 1;

  min-height: 0;

}


/* =====================================================
   标题
===================================================== */

.panel-title {

  height: 42px;

  display: flex;

  align-items: center;

  padding-left: 18px;

  font-size: 15px;

  font-weight: 600;

  letter-spacing: 1px;

  color: #dffaff;

}


.panel-title span {

  display: inline-block;

  width: 5px;

  height: 17px;

  margin-right: 10px;

  background:
    linear-gradient(
      180deg,
      #72efff,
      #1883b2
    );

  box-shadow:
    0 0 10px
    rgba(
      65,
      221,
      255,
      0.8
    );

}


/* =====================================================
   图表
===================================================== */

.chart-image-wrapper {

  position: absolute;

  left: 4%;

  right: 4%;

  top: 45px;

  bottom: 4%;

  display: flex;

  align-items: center;

  justify-content: center;

}


.chart-image-wrapper img {

  width: 100%;

  height: 100%;

  object-fit: contain;

}


/* =====================================================
   点击
===================================================== */

.clickable {

  cursor: pointer;

  transition:
    transform 0.25s ease,
    border-color 0.25s ease,
    box-shadow 0.25s ease;

}


.clickable:hover {

  transform:
    translateY(-2px)
    scale(1.005);

  border-color:
    rgba(
      80,
      225,
      255,
      0.65
    );

  box-shadow:
    0 0 25px
    rgba(
      20,
      190,
      230,
      0.15
    );

}


/* =====================================================
   地图
===================================================== */

.map-panel {

  width: 100%;

  height: 100%;

}


.map-container {

  position: absolute;

  left: 0;

  right: 0;

  top: 42px;

  bottom: 0;

}


.map-title {

  position: relative;

  z-index: 20;

}


.expand-button {

  margin-left: auto;

  margin-right: 15px;

  border: none;

  background: transparent;

  color: #78e8ff;

  font-size: 20px;

  cursor: pointer;

}


/* =====================================================
   弹窗
===================================================== */

.modal {

  position: fixed;

  inset: 0;

  z-index: 9999;

  background:
    rgba(
      0,
      5,
      12,
      0.88
    );

  backdrop-filter:
    blur(8px);

  display: flex;

  align-items: center;

  justify-content: center;

  padding: 3vw;

}


.modal-content {

  width: 94vw;

  height: 90vh;

  background:
    linear-gradient(
      135deg,
      rgba(
        4,
        28,
        48,
        0.98
      ),
      rgba(
        2,
        14,
        27,
        0.98
      )
    );

  border:
    1px solid
    rgba(
      78,
      217,
      247,
      0.4
    );

  border-radius: 12px;

  overflow: hidden;

  box-shadow:
    0 0 80px
    rgba(
      0,
      180,
      230,
      0.18
    );

}


.modal-header {

  height: 60px;

  display: flex;

  align-items: center;

  justify-content: space-between;

  padding: 0 25px;

  border-bottom:
    1px solid
    rgba(
      80,
      210,
      240,
      0.15
    );

}


.modal-title {

  font-size: 20px;

  font-weight: 600;

  color: #e5fbff;

}


.close-button {

  width: 40px;

  height: 40px;

  border: none;

  border-radius: 50%;

  background:
    rgba(
      255,
      255,
      255,
      0.06
    );

  color: white;

  font-size: 28px;

  cursor: pointer;

}


.close-button:hover {

  background:
    rgba(
      255,
      255,
      255,
      0.15
    );

}


.modal-body {

  height:
    calc(
      100% - 60px
    );

  padding: 20px;

  display: flex;

  align-items: center;

  justify-content: center;

}


.modal-body img {

  width: 100%;

  height: 100%;

  object-fit: contain;

}


.modal-map {

  width: 100%;

  height: 100%;

}


/* =====================================================
   底部
===================================================== */

.footer {

  height: 5%;

  display: flex;

  justify-content: center;

  align-items: center;

  font-size: 11px;

  color:
    rgba(
      160,
      220,
      235,
      0.5
    );

  letter-spacing: 1px;

}


.footer span {

  margin: 0 10px;

}


/* =====================================================
   响应式
===================================================== */

@media (
  max-width: 1200px
) {

  .dashboard-main {

    grid-template-columns:
      1fr;

    overflow-y: auto;

  }

  .dashboard {

    height: auto;

    min-height: 100vh;

    overflow: auto;

  }

  .left-column,
  .right-column,
  .center-column {

    min-height: 500px;

  }

}
</style>