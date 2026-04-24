package com.accounting.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.accounting.app.ui.theme.AppColors
import com.accounting.app.viewmodel.StatsViewModel
import java.util.*

@Composable
fun StatsScreen(
    onNavigateToBalanceTrend: () -> Unit = {}
) {
    val statsViewModel: StatsViewModel = viewModel()
    val overview by statsViewModel.overview.collectAsState()
    val categoryStats by statsViewModel.categoryStats.collectAsState()
    val trendData by statsViewModel.trendData.collectAsState()
    val loading by statsViewModel.loading.collectAsState()

    var currentYear by remember { mutableIntStateOf(Calendar.getInstance().get(Calendar.YEAR)) }
    var currentMonth by remember { mutableIntStateOf(Calendar.getInstance().get(Calendar.MONTH) + 1) }

    fun loadStats() {
        val m = String.format("%02d", currentMonth)
        val start = "$currentYear-$m-01"
        val lastDay = when (currentMonth) {
            2 -> if (currentYear % 4 == 0 && (currentYear % 100 != 0 || currentYear % 400 == 0)) 29 else 28
            4, 6, 9, 11 -> 30
            else -> 31
        }
        val end = "$currentYear-$m-$lastDay"
        statsViewModel.loadStats(start, end)
    }

    LaunchedEffect(Unit) { loadStats() }
    LaunchedEffect(currentYear, currentMonth) { loadStats() }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 20.dp)
            .verticalScroll(rememberScrollState())
            .padding(top = 16.dp, bottom = 80.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                "统计",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onBackground
            )
            TextButton(onClick = onNavigateToBalanceTrend) {
                Text("余额趋势 →", fontSize = 13.sp, color = MaterialTheme.colorScheme.primary)
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(
                onClick = {
                    if (currentMonth == 1) { currentMonth = 12; currentYear-- }
                    else currentMonth--
                },
                modifier = Modifier
                    .size(36.dp)
                    .clip(CircleShape)
                    .background(AppColors.cardBg)
            ) {
                Text("‹", fontSize = 20.sp, color = MaterialTheme.colorScheme.onBackground)
            }
            Spacer(modifier = Modifier.width(20.dp))
            Text(
                "${currentYear}年${currentMonth}月",
                fontSize = 16.sp,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.onBackground
            )
            Spacer(modifier = Modifier.width(20.dp))
            IconButton(
                onClick = {
                    if (currentMonth == 12) { currentMonth = 1; currentYear++ }
                    else currentMonth++
                },
                modifier = Modifier
                    .size(36.dp)
                    .clip(CircleShape)
                    .background(AppColors.cardBg)
            ) {
                Text("›", fontSize = 20.sp, color = MaterialTheme.colorScheme.onBackground)
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        if (overview != null) {
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Card(
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = AppColors.cardBg)
                ) {
                    Column(modifier = Modifier.padding(20.dp)) {
                        Text("收入", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            "¥${formatMoney(overview!!.total_income)}",
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            color = AppColors.incomeColor
                        )
                    }
                }
                Card(
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = AppColors.cardBg)
                ) {
                    Column(modifier = Modifier.padding(20.dp)) {
                        Text("支出", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            "¥${formatMoney(overview!!.total_expense)}",
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            color = AppColors.expenseColor
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        Text(
            "支出分类",
            fontSize = 13.sp,
            fontWeight = FontWeight.SemiBold,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(modifier = Modifier.height(12.dp))

        if (categoryStats.isNotEmpty()) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = AppColors.cardBg)
            ) {
                Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                    categoryStats.forEach { stat ->
                        Column {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    stat.category_name,
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = MaterialTheme.colorScheme.onBackground
                                )
                                Text(
                                    "¥${formatMoney(stat.amount)}",
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = MaterialTheme.colorScheme.onBackground
                                )
                            }
                            Spacer(modifier = Modifier.height(6.dp))
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(6.dp)
                                    .clip(RoundedCornerShape(3.dp))
                                    .background(AppColors.inputBg)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .fillMaxHeight()
                                        .fillMaxWidth(stat.percentage.toFloat() / 100f)
                                        .clip(RoundedCornerShape(3.dp))
                                        .background(
                                            when {
                                                stat.percentage > 40 -> AppColors.barColorHigh
                                                stat.percentage > 25 -> AppColors.barColorMedium
                                                stat.percentage > 15 -> AppColors.barColorLow
                                                else -> AppColors.barColorDefault
                                            }
                                        )
                                )
                            }
                            Text(
                                "${stat.percentage}%",
                                fontSize = 11.sp,
                                color = AppColors.textMuted,
                                modifier = Modifier.align(Alignment.End)
                            )
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        Text(
            "收支趋势",
            fontSize = 13.sp,
            fontWeight = FontWeight.SemiBold,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(modifier = Modifier.height(12.dp))

        if (trendData.isNotEmpty()) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = AppColors.cardBg)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    val maxVal = trendData.maxOfOrNull { maxOf(it.income, it.expense) } ?: 1.0

                    trendData.takeLast(7).forEach { item ->
                        val period = item.period.substring(5)
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                period,
                                fontSize = 11.sp,
                                color = AppColors.textMuted,
                                modifier = Modifier.width(40.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))

                            if (item.income > 0) {
                                Box(
                                    modifier = Modifier
                                        .weight(item.income.toFloat() / maxVal.toFloat())
                                        .height(12.dp)
                                        .clip(RoundedCornerShape(3.dp))
                                        .background(AppColors.incomeColor.copy(alpha = 0.7f))
                                )
                            }
                            Spacer(modifier = Modifier.width(4.dp))
                            if (item.expense > 0) {
                                Box(
                                    modifier = Modifier
                                        .weight(item.expense.toFloat() / maxVal.toFloat())
                                        .height(12.dp)
                                        .clip(RoundedCornerShape(3.dp))
                                        .background(AppColors.expenseColor.copy(alpha = 0.7f))
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(12.dp))
                    Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(
                                modifier = Modifier
                                    .size(8.dp)
                                    .clip(CircleShape)
                                    .background(AppColors.incomeColor)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("收入", fontSize = 11.sp, color = AppColors.textMuted)
                        }
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(
                                modifier = Modifier
                                    .size(8.dp)
                                    .clip(CircleShape)
                                    .background(AppColors.expenseColor)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("支出", fontSize = 11.sp, color = AppColors.textMuted)
                        }
                    }
                }
            }
        }
    }
}

