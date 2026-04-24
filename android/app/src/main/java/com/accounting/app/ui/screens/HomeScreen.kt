package com.accounting.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
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
import com.accounting.app.api.*
import com.accounting.app.ui.theme.AppColors
import com.accounting.app.viewmodel.BillViewModel
import com.accounting.app.viewmodel.DataViewModel
import com.accounting.app.viewmodel.StatsViewModel
import java.text.SimpleDateFormat
import java.util.*

fun formatMoney(n: Double): String {
    return String.format("%,.2f", kotlin.math.abs(n))
}

fun getCategoryIcon(categoryId: Int): String {
    val iconMap = mapOf(
        1 to "🍜", 2 to "🚌", 3 to "🛒", 4 to "🏠", 5 to "🎮",
        6 to "🏥", 7 to "📚", 8 to "📱", 9 to "🎁", 10 to "📌",
        46 to "💰", 47 to "💼", 48 to "📈", 49 to "🧧", 50 to "↩️", 51 to "📌"
    )
    val parentId = (categoryId / 10) * 10
    return iconMap[categoryId] ?: iconMap[parentId] ?: "📌"
}

fun getMonthRange(): Pair<String, String> {
    val cal = Calendar.getInstance()
    val year = cal.get(Calendar.YEAR)
    val month = cal.get(Calendar.MONTH)
    val start = String.format("%d-%02d-01", year, month + 1)
    val lastDay = cal.getActualMaximum(Calendar.DAY_OF_MONTH)
    val end = String.format("%d-%02d-%02d", year, month + 1, lastDay)
    return Pair(start, end)
}

@Composable
fun HomeScreen(
    onNavigateToBills: () -> Unit,
    onNavigateToAdd: () -> Unit,
    onNavigateToSettings: () -> Unit = {},
    onNavigateToAi: () -> Unit = {},
    onLogout: () -> Unit
) {
    val dataViewModel: DataViewModel = viewModel()
    val billViewModel: BillViewModel = viewModel()
    val statsViewModel: StatsViewModel = viewModel()

    val accounts by dataViewModel.accounts.collectAsState()
    val bills by billViewModel.bills.collectAsState()
    val overview by statsViewModel.overview.collectAsState()

    LaunchedEffect(Unit) {
        dataViewModel.loadAll()
        val (start, end) = getMonthRange()
        billViewModel.loadBills(page = 1, size = 5, startDate = start, endDate = end)
        statsViewModel.loadStats(start, end)
    }

    val todayStr = remember {
        SimpleDateFormat("M月d日 E", Locale.CHINESE).format(Date())
    }

    Box(modifier = Modifier.fillMaxSize()) {
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 20.dp)
                .padding(top = 16.dp)
                .padding(bottom = 80.dp)
        ) {
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        "记账",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onBackground
                    )
                    Text(
                        todayStr,
                        fontSize = 13.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    TextButton(onClick = onNavigateToSettings) {
                        Text("⚙", fontSize = 18.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
                Spacer(modifier = Modifier.height(20.dp))
            }

            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = AppColors.overviewCardBg
                    )
                ) {
                    Column(modifier = Modifier.padding(20.dp)) {
                        Text(
                            "本月结余",
                            fontSize = 13.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            "¥${formatMoney(overview?.balance ?: 0.0)}",
                            fontSize = 36.sp,
                            fontWeight = FontWeight.ExtraBold,
                            color = if ((overview?.balance ?: 0.0) >= 0) AppColors.incomeColor else AppColors.expenseColor,
                            letterSpacing = (-1).sp
                        )
                        Spacer(modifier = Modifier.height(20.dp))
                        Row(horizontalArrangement = Arrangement.spacedBy(24.dp)) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Box(
                                    modifier = Modifier
                                        .size(8.dp)
                                        .clip(CircleShape)
                                        .background(AppColors.incomeColor)
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text("收入", fontSize = 13.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                Spacer(modifier = Modifier.width(4.dp))
                                Text(
                                    "¥${formatMoney(overview?.total_income ?: 0.0)}",
                                    fontSize = 15.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = AppColors.incomeColor
                                )
                            }
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Box(
                                    modifier = Modifier
                                        .size(8.dp)
                                        .clip(CircleShape)
                                        .background(AppColors.expenseColor)
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text("支出", fontSize = 13.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                Spacer(modifier = Modifier.width(4.dp))
                                Text(
                                    "¥${formatMoney(overview?.total_expense ?: 0.0)}",
                                    fontSize = 15.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = AppColors.expenseColor
                                )
                            }
                        }
                    }
                }
                Spacer(modifier = Modifier.height(28.dp))
            }

            item {
                Text(
                    "最近账单",
                    fontSize = 13.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(12.dp))
            }

            if (bills.isEmpty()) {
                item {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 48.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text("📝", fontSize = 48.sp)
                        Spacer(modifier = Modifier.height(12.dp))
                        Text(
                            "暂无账单，点击下方记账开始",
                            fontSize = 14.sp,
                            color = AppColors.textMuted
                        )
                    }
                }
            } else {
                items(bills) { bill ->
                    BillItem(
                        bill = bill,
                        onClick = { onNavigateToBills() }
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                }
            }
        }

        FloatingActionButton(
            onClick = onNavigateToAdd,
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(end = 20.dp, bottom = 96.dp),
            containerColor = MaterialTheme.colorScheme.primary,
            shape = CircleShape
        ) {
            Text("+", fontSize = 28.sp, color = MaterialTheme.colorScheme.onPrimary)
        }

        SmallFloatingActionButton(
            onClick = onNavigateToAi,
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(end = 20.dp, bottom = 160.dp),
            containerColor = MaterialTheme.colorScheme.secondary,
            shape = CircleShape
        ) {
            Text("🤖", fontSize = 16.sp)
        }
    }
}

@Composable
fun BillItem(bill: Bill, onClick: () -> Unit = {}) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = AppColors.cardBg)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(AppColors.inputBg),
                contentAlignment = Alignment.Center
            ) {
                Text(getCategoryIcon(bill.category_id), fontSize = 20.sp)
            }
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    bill.category_name,
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.onBackground
                )
                Text(
                    "${bill.account_name}${if (bill.remark.isNotEmpty()) " · ${bill.remark}" else ""}",
                    fontSize = 12.sp,
                    color = AppColors.textMuted,
                    maxLines = 1
                )
            }
            Text(
                "${if (bill.type == 2) "+" else "-"}¥${formatMoney(bill.amount)}",
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = if (bill.type == 2) AppColors.incomeColor else AppColors.expenseColor
            )
        }
    }
}
