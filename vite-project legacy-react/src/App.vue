<template>
  <div>
    <h1>ファイルドロップアプリへようこそ！</h1>

    <div
      id="drop-area"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      :class="{ 'dragging': isDragging }"
    >
      ここにファイルをドロップしてください
    </div>
    <div v-if="fileContent.length" style="margin-top: 40px;">
  <h2>売上数グラフ</h2>
  <canvas id="sales-chart"></canvas>
</div>


    <div v-if="uploadedFileName">
      <h2>受け取ったファイル名：</h2>
      <p>{{ uploadedFileName }}</p>
    </div>

    <div v-if="fileContent.length">
      <h2>ファイルの中身：</h2>
      <div v-if="fileContent.length">
  <h2>ファイルの中身（テーブル表示）：</h2>
  <table>
    <thead>
      <tr>
        <th v-for="(header, index) in Object.keys(fileContent[0])" :key="index">
          {{ header }}
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(row, rowIndex) in fileContent" :key="rowIndex">
        <td v-for="(value, colIndex) in row" :key="colIndex">
          {{ value }}
        </td>
      </tr>
    </tbody>
  </table>
  <div v-if="bestSellers.length && worstSellers.length" style="margin-top: 40px;">
  <h2>ランキングレポート</h2>
  <div style="display: flex; justify-content: center; gap: 40px; margin-top: 20px;">
    
    <div>
      <h3>売れ筋ランキング</h3>
      <table>
        <thead>
          <tr>
            <th>順位</th>
            <th>商品名</th>
            <th>売上数</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in bestSellers" :key="'best-' + index">
            <td>{{ index + 1 }}</td>
            <td>{{ item['商品名'] }}</td>
            <td>{{ item['売上数'] }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div>
      <h3>死に筋ランキング</h3>
      <table>
        <thead>
          <tr>
            <th>順位</th>
            <th>商品名</th>
            <th>売上数</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in worstSellers" :key="'worst-' + index">
            <td>{{ index + 1 }}</td>
            <td>{{ item['商品名'] }}</td>
            <td>{{ item['売上数'] }}</td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</div>

</div>


    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import * as XLSX from 'xlsx'

const isDragging = ref(false)
const uploadedFileName = ref('')
const fileContent = ref([])

function handleDrop(event) {
  const files = event.dataTransfer.files
  if (files.length > 0) {
    uploadedFileName.value = files[0].name
    readFile(files[0])
  }
  isDragging.value = false
}

function readFile(file) {
  const reader = new FileReader()
  reader.onload = (e) => {
    const data = new Uint8Array(e.target.result)
    const workbook = XLSX.read(data, { type: 'array' })
    const firstSheetName = workbook.SheetNames[0]
    const worksheet = workbook.Sheets[firstSheetName]
    const jsonData = XLSX.utils.sheet_to_json(worksheet)
    console.log('読み取ったデータ:', jsonData)
    fileContent.value = jsonData
  }
  reader.readAsArrayBuffer(file)
}
import { computed } from 'vue'

// ファイルから読み込んだデータからランキングを作る
const bestSellers = computed(() => {
  return [...fileContent.value]
    .sort((a, b) => b['売上数'] - a['売上数'])
    .slice(0, 5) // 上位5件だけ表示
})

const worstSellers = computed(() => {
  return [...fileContent.value]
    .sort((a, b) => a['売上数'] - b['売上数'])
    .slice(0, 5) // 下位5件だけ表示
})
import { onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

let salesChart = null

// fileContentが変わったらグラフを更新する
watch(fileContent, (newData) => {
  if (!newData.length) return

  const ctx = document.getElementById('sales-chart').getContext('2d')

  // すでにグラフが存在してたら破棄してから作り直す
  if (salesChart) {
    salesChart.destroy()
  }

  salesChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: newData.map(item => item['商品名']),
      datasets: [{
        label: '売上数',
        data: newData.map(item => item['売上数']),
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        boraaderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  })
})


</script>

<style scoped>
#drop-area {
  width: 80%;
  height: 200px;
  border: 2px dashed #6cb4ee;
  border-radius: 20px;
  margin: 50px auto;
  text-align: center;
  line-height: 200px;
  font-size: 18px;
  color: #666;
  background-color: #f0f8ff;
  transition: background-color 0.3s;
}

#drop-area.dragging {
  background-color: #e0f7fa;
  table {
  width: 80%;
  margin: 20px auto;
  border-collapse: collapse;
}

th, td {
  border: 1px solid #ccc;
  padding: 8px 12px;
  text-align: center;
}

thead {
  background-color: #e0f7fa;
}

}
</style>
