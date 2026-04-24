package com.accounting.app.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.accounting.app.api.*
import com.accounting.app.ui.theme.AppColors
import com.accounting.app.viewmodel.StatsViewModel
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BalanceTrendScreen(
    onBack: () -> Unit = {}
) {
    val statsViewModel: StatsViewModel = viewModel()
    val trendData by statsViewModel.trendData.collectAsState()

    var selectedRange by remember { mutableIntStateOf(1) }
    val ranges = listOf("1周" to 7, "1月" to 30, "3月" to 90, "6月" to 180, "1年" to 365)

    LaunchedEffect(selectedRange) {
        val cal = Calendar.getInstance()
        val endDate = SimpleDateFormat("yyyy-MM-dd", Locale.CHINESE).format(cal.time)
        cal.add(Calendar.DAY_OF_YEAR, -ranges[selectedRange].second)
        val startDate = SimpleDateFormat("yyyy-MM-dd", Locale.CHINESE).format(cal.time)
        statsViewModel.loadStats(startDate, endDate)
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 20.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 16.dp, bottom = 24.dp),
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
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            modifier = Modifier.fillMaxWidth()
        ) {
            ranges.forEachIndexed { index, (label, _) ->
                FilterChip(
                    selected = selectedRange == index,
                    onClick = { selectedRange = index },
                    label = { Text(label, fontSize = 12.sp) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = AppColors.primaryBgColor,
                        selectedLabelColor = MaterialTheme.colorScheme.primary
                    )
                )
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        if (trendData.isEmpty()) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Text("暂无趋势数据", color = AppColors.textMuted)
            }
        } else {
            LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                items(trendData.sortedByDescending { it.period }) { item ->
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(containerColor = AppColors.cardBg)
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                item.period,
                                fontSize = 14.sp,
                                color = MaterialTheme.colorScheme.onBackground
                            )
                            Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                                Text(
                                    "收入 ¥${String.format("%.0f", item.income)}",
                                    fontSize = 13.sp,
                                    color = AppColors.incomeColor
                                )
                                Text(
                                    "支出 ¥${String.format("%.0f", item.expense)}",
                                    fontSize = 13.sp,
                                    color = AppColors.expenseColor
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
