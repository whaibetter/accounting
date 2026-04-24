export function formatMoney(amount, showSign = false) {
  const num = Number(amount) || 0
  const formatted = num.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
  if (showSign && num > 0) return '+' + formatted
  return formatted
}

export function formatMoneyWithSymbol(amount, showSign = false) {
  return '¥ ' + formatMoney(amount, showSign)
}

export function formatDate(date) {
  return dayjs(date).format('YYYY-MM-DD')
}

export function formatDateCN(date) {
  return dayjs(date).format('M月D日')
}

export function formatMonth(date) {
  return dayjs(date).format('YYYY年M月')
}

export function getWeekday(date) {
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return weekdays[dayjs(date).day()]
}

export function getBillTypeName(type) {
  const map = { 1: '支出', 2: '收入', 3: '转账' }
  return map[type] || '未知'
}

export function getAccountTypeName(type) {
  const map = { 1: '现金', 2: '银行卡', 3: '信用卡', 4: '支付宝', 5: '微信', 6: '其他' }
  return map[type] || '未知'
}

export function getAccountTypeColor(type) {
  const map = {
    1: '#d4a574',
    2: '#7cafd4',
    3: '#d47b7b',
    4: '#7bc97b',
    5: '#7b9bd4',
    6: '#c4b896',
  }
  return map[type] || '#ccc'
}

export function getCategoryIcon(icon) {
  return icon || '📝'
}

import dayjs from 'dayjs'

export function getMonthRange(date) {
  const d = dayjs(date)
  return {
    start_date: d.startOf('month').format('YYYY-MM-DD'),
    end_date: d.endOf('month').format('YYYY-MM-DD'),
  }
}

export function debounce(fn, delay = 300) {
  let timer
  return function (...args) {
    clearTimeout(timer)
    timer = setTimeout(() => fn.apply(this, args), delay)
  }
}

export const CATEGORY_COLORS = [
  '#d4a574', '#e8c99a', '#f0d9b8', '#dccaa8',
  '#7cafd4', '#7bc97b', '#d47b7b', '#a07bd4',
  '#c4b896', '#7b9bd4',
]
