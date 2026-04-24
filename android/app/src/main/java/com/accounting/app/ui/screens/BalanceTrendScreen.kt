package com.accounting.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.accounting.app.api.AccountBalanceTrend
import com.accounting.app.api.ApiClient
import com.accounting.app.ui.theme.AppColors

data class TimeFilterOption(val label: String, val value: String)

val timeFilterOptions = listOf(
    TimeFilterOption("1周", "1w"),
    TimeFilterOption("1月", "1m"),
    TimeFilterOption("3月", "3m"),
    TimeFilterOption("6月", "6m"),
    TimeFilterOption("1年", "1y"),
    TimeFilterOption("2年", "2y"),
)

val accountTypeOptions = listOf(
    "全部类型" to 0,
    "现金" to 1,
    "银行卡" to 2,
    "信用卡" to 3,
    "支付宝" to 4,
    "微信" to 5,
    "其他" to 6,
)

fun getDateRangeForFilter(filter: String): Pair<String, String> {
    val cal = java.util.Calendar.getInstance()
    val end = String.format("%tF", cal)
    when (filter) {
        "1w" -> cal.add(java.util.Calendar.DAY_OF_YEAR, -7)
        "1m" -> cal.add(java.util.Calendar.MONTH, -1)
        "3m" -> cal.add(java.util.Calendar.MONTH, -3)
        "6m" -> cal.add(java.util.Calendar.MONTH, -6)
        "1y" -> cal.add(java.util.Calendar.YEAR, -1)
        "2y" -> cal.add(java.util.Calendar.YEAR, -2)
    }
    val start = String.format("%tF", cal)
    return Pair(start, end)
}

fun parseColor(hex: String): Color {
    return try {
        val cleaned = hex.removePrefix("#")
        val alpha = if (cleaned.length == 8) cleaned.substring(6, 8).toInt(16) else 255
        val red = cleaned.substring(0, 2).toInt(16)
        val green = cleaned.substring(2, 4).toInt(16)
        val blue = cleaned.substring(4, 6).toInt(16)
        Color(red, green, blue, alpha)
    } catch (e: Exception) {
        Color(0xFF6366f1.toInt())
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BalanceTrendScreen(onBack: () -> Unit) {
    var selectedTimeFilter by remember { mutableStateOf("1m") }
    var selectedAccountType by remember { mutableStateOf(0) }
    var selectedAccountId by remember { mutableIntStateOf(0) }
    var balanceData by remember { mutableStateOf<List<AccountBalanceTrend>>(emptyList()) }
    var loading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(selectedTimeFilter, selectedAccountType, selectedAccountId) {
        loading = true
        error = null
        try {
            val (start, end) = getDateRangeForFilter(selectedTimeFilter)
            val response = ApiClient.api.getBalanceTrend(
                startDate = start,
                endDate = end,
                accountId = if (selectedAccountId > 0) selectedAccountId else null,
                accountType = if (selectedAccountType > 0) selectedAccountType else null
            )
            balanceData = response.data ?: emptyList()
        } catch (e: Exception) {
            error = e.message ?: "加载失败"
            balanceData = emptyList()
        } finally {
            loading = false
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 20.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 16.dp, bottom = 20.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            TextButton(onClick = onBack) {
                Text("← 返回", color = MaterialTheme.colorScheme.primary)
            }
            Spacer(modifier = Modifier.weight(1f))
            Text(
                "余额趋势",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onBackground
            )
            Spacer(modifier = Modifier.weight(1f))
            Spacer(modifier = Modifier.width(48.dp))
        }

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            timeFilterOptions.forEach { tf ->
                FilterChip(
                    selected = selectedTimeFilter == tf.value,
                    onClick = { selectedTimeFilter = tf.value },
                    label = { Text(tf.label, fontSize = 12.sp) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = MaterialTheme.colorScheme.primary,
                        selectedLabelColor = Color.White
                    )
                )
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            var typeExpanded by remember { mutableStateOf(false) }
            val selectedTypeName = accountTypeOptions.find { it.second == selectedAccountType }?.first ?: "全部类型"

            Box {
                OutlinedButton(
                    onClick = { typeExpanded = true },
                    shape = RoundedCornerShape(8.dp),
                    modifier = Modifier.weight(1f)
                ) {
                    Text(selectedTypeName, fontSize = 13.sp, color = MaterialTheme.colorScheme.onBackground)
                }
                DropdownMenu(expanded = typeExpanded, onDismissRequest = { typeExpanded = false }) {
                    accountTypeOptions.forEach { (name, value) ->
                        DropdownMenuItem(
                            text = { Text(name) },
                            onClick = {
                                selectedAccountType = value
                                selectedAccountId = 0
                                typeExpanded = false
                            }
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        when {
            loading -> {
                Box(modifier = Modifier.fillMaxWidth().height(200.dp), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
            }
            error != null -> {
                Box(modifier = Modifier.fillMaxWidth().height(200.dp), contentAlignment = Alignment.Center) {
                    Text(error ?: "", color = MaterialTheme.colorScheme.error)
                }
            }
            balanceData.isEmpty() -> {
                Box(modifier = Modifier.fillMaxWidth().height(200.dp), contentAlignment = Alignment.Center) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("📊", fontSize = 48.sp)
                        Spacer(modifier = Modifier.height(8.dp))
                        Text("暂无数据", color = AppColors.textMuted)
                    }
                }
            }
            else -> {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    balanceData.forEach { account ->
                        val isSelected = selectedAccountId == account.account_id
                        Card(
                            shape = RoundedCornerShape(12.dp),
                            colors = CardDefaults.cardColors(
                                containerColor = if (isSelected)
                                    MaterialTheme.colorScheme.primaryContainer
                                else
                                    AppColors.cardBg
                            ),
                            modifier = Modifier.clickable {
                                selectedAccountId =
                                    if (selectedAccountId == account.account_id) 0 else account.account_id
                            }
                        ) {
                            Row(
                                modifier = Modifier.padding(10.dp, 8.dp),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(6.dp)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(8.dp)
                                        .background(parseColor(account.color), RoundedCornerShape(4.dp))
                                )
                                Column {
                                    Text(
                                        account.account_name,
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.Medium,
                                        color = MaterialTheme.colorScheme.onBackground
                                    )
                                    Text(
                                        account.account_type_name,
                                        fontSize = 9.sp,
                                        color = AppColors.textMuted
                                    )
                                }
                                Text(
                                    "¥${formatMoney(account.current_balance)}",
                                    fontSize = 13.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = if (account.current_balance < 0) AppColors.expenseColor else MaterialTheme.colorScheme.onBackground
                                )
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = AppColors.cardBg)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            "余额变化",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = MaterialTheme.colorScheme.onBackground
                        )
                        Spacer(modifier = Modifier.height(12.dp))

                        val displayData = balanceData.firstOrNull()?.data ?: emptyList()
                        if (displayData.isNotEmpty()) {
                            val maxBalance = balanceData.maxOf { acc -> acc.data.maxOfOrNull { it.balance } ?: 0.0 }
                            val minBalance = balanceData.minOf { acc -> acc.data.minOfOrNull { it.balance } ?: 0.0 }
                            val range = (maxBalance - minBalance).let { if (it == 0.0) 1.0 else it }
                            val chartHeight = 180.dp

                            Box(modifier = Modifier.fillMaxWidth().height(chartHeight)) {
                                val gridLines = 4
                                for (i in 0..gridLines) {
                                    val yFrac = i.toFloat() / gridLines
                                    val value = maxBalance - (range * yFrac)
                                    Box(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .height(1.dp)
                                            .background(AppColors.inputBg)
                                            .offset(y = (chartHeight * yFrac))
                                    )
                                    Text(
                                        if (kotlin.math.abs(value) >= 10000) "%.1fw".format(value / 10000)
                                        else if (kotlin.math.abs(value) >= 1000) "%.1fk".format(value / 1000)
                                        else "%.0f".format(value),
                                        fontSize = 9.sp,
                                        color = AppColors.textMuted,
                                        modifier = Modifier.offset(y = (chartHeight * yFrac) - 6.dp)
                                    )
                                }

                                balanceData.forEach { account ->
                                    val points = account.data.mapIndexed { index, item ->
                                        val xFrac = if (displayData.size <= 1) 0.5f else index.toFloat() / (displayData.size - 1)
                                        val yFrac = ((maxBalance - item.balance) / range).toFloat().coerceIn(0f, 1f)
                                        xFrac to yFrac
                                    }

                                    if (points.size >= 2) {
                                        androidx.compose.foundation.canvas.Canvas(
                                            modifier = Modifier.fillMaxSize()
                                        ) {
                                            val path = androidx.compose.ui.graphics.Path()
                                            val firstPoint = points.first()
                                            path.moveTo(
                                                size.width * firstPoint.first,
                                                size.height * firstPoint.second
                                            )
                                            for (i in 1 until points.size) {
                                                path.lineTo(
                                                    size.width * points[i].first,
                                                    size.height * points[i].second
                                                )
                                            }
                                            drawPath(
                                                path = path,
                                                color = parseColor(account.color),
                                                style = androidx.compose.ui.graphics.drawscope.Stroke(
                                                    width = 2.dp.toPx()
                                                )
                                            )
                                        }
                                    }
                                }
                            }

                            Spacer(modifier = Modifier.height(8.dp))

                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                val step = maxOf(1, displayData.size / 6)
                                displayData.forEachIndexed { index, item ->
                                    if (index % step == 0 || index == displayData.size - 1) {
                                        Text(
                                            item.date.substring(5),
                                            fontSize = 9.sp,
                                            color = AppColors.textMuted
                                        )
                                    }
                                }
                            }
                        }
                    }
                }

                val detailAccount = if (selectedAccountId > 0) {
                    balanceData.find { it.account_id == selectedAccountId }
                } else {
                    balanceData.firstOrNull()
                }

                if (detailAccount != null && detailAccount.data.isNotEmpty()) {
                    Spacer(modifier = Modifier.height(20.dp))

                    Text(
                        "${detailAccount.account_name} - 收支明细",
                        fontSize = 15.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = MaterialTheme.colorScheme.onBackground
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        StatCard("期初余额", "¥${formatMoney(detailAccount.data.first().balance)}", Modifier.weight(1f))
                        StatCard("期末余额", "¥${formatMoney(detailAccount.data.last().balance)}", Modifier.weight(1f))
                    }
                    Spacer(modifier = Modifier.height(10.dp))
                    val totalIncome = detailAccount.data.sumOf { it.income }
                    val totalExpense = detailAccount.data.sumOf { it.expense }
                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        StatCard("总收入", "¥${formatMoney(totalIncome)}", Modifier.weight(1f), AppColors.incomeColor)
                        StatCard("总支出", "¥${formatMoney(totalExpense)}", Modifier.weight(1f), AppColors.expenseColor)
                    }
                }
            }
        }
    }
}

@Composable
private fun StatCard(label: String, value: String, modifier: Modifier = Modifier, valueColor: Color? = null) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = AppColors.cardBg)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(label, fontSize = 11.sp, color = AppColors.textMuted)
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                value,
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = valueColor ?: MaterialTheme.colorScheme.onBackground
            )
        }
    }
}
