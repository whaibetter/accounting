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
import com.accounting.app.api.Bill
import com.accounting.app.api.BillUpdate
import com.accounting.app.ui.theme.*
import com.accounting.app.viewmodel.BillViewModel
import com.accounting.app.viewmodel.DataViewModel
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BillsScreen(
    onNavigateToAdd: () -> Unit,
    onNavigateToEdit: (Int) -> Unit
) {
    val billViewModel: BillViewModel = viewModel()
    val dataViewModel: DataViewModel = viewModel()
    val bills by billViewModel.bills.collectAsState()

    var currentYear by remember { mutableIntStateOf(Calendar.getInstance().get(Calendar.YEAR)) }
    var currentMonth by remember { mutableIntStateOf(Calendar.getInstance().get(Calendar.MONTH) + 1) }
    var currentFilter by remember { mutableIntStateOf(0) }

    val filters = listOf(0 to "全部", 1 to "支出", 2 to "收入")

    LaunchedEffect(Unit) {
        dataViewModel.loadAll()
    }

    LaunchedEffect(currentYear, currentMonth, currentFilter) {
        val m = String.format("%02d", currentMonth)
        val start = "$currentYear-$m-01"
        val lastDay = when (currentMonth) {
            2 -> if (currentYear % 4 == 0 && (currentYear % 100 != 0 || currentYear % 400 == 0)) 29 else 28
            4, 6, 9, 11 -> 30
            else -> 31
        }
        val end = "$currentYear-$m-$lastDay"
        billViewModel.loadBills(
            page = 1, size = 100,
            startDate = start, endDate = end,
            type = if (currentFilter > 0) currentFilter else null
        )
    }

    var showEditDialog by remember { mutableStateOf(false) }
    var editBill by remember { mutableStateOf<Bill?>(null) }
    var editAmount by remember { mutableStateOf("") }
    var editRemark by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 20.dp)
            .padding(top = 16.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                "账单",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onBackground
            )
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                filters.forEach { (value, label) ->
                    FilterChip(
                        selected = currentFilter == value,
                        onClick = { currentFilter = value },
                        label = { Text(label, fontSize = 13.sp) },
                        shape = RoundedCornerShape(20.dp),
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = PrimaryBgColor,
                            selectedLabelColor = MaterialTheme.colorScheme.secondary
                        ),
                        border = FilterChipDefaults.filterChipBorder(
                            borderColor = BorderColor,
                            selectedBorderColor = MaterialTheme.colorScheme.primary
                        )
                    )
                }
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
                    .background(CardBg)
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
                    .background(CardBg)
            ) {
                Text("›", fontSize = 20.sp, color = MaterialTheme.colorScheme.onBackground)
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        if (bills.isEmpty()) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 48.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text("📭", fontSize = 48.sp)
                Spacer(modifier = Modifier.height(12.dp))
                Text("本月暂无账单", fontSize = 14.sp, color = TextMuted)
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(bottom = 80.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(bills) { bill ->
                    BillItem(
                        bill = bill,
                        onClick = {
                            editBill = bill
                            editAmount = bill.amount.toString()
                            editRemark = bill.remark
                            showEditDialog = true
                        }
                    )
                }
            }
        }
    }

    if (showEditDialog && editBill != null) {
        AlertDialog(
            onDismissRequest = { showEditDialog = false },
            title = { Text("编辑账单") },
            containerColor = CardBg,
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                    OutlinedTextField(
                        value = editAmount,
                        onValueChange = { editAmount = it },
                        label = { Text("金额") },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(10.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = MaterialTheme.colorScheme.primary,
                            unfocusedBorderColor = BorderColor,
                            focusedContainerColor = InputBg,
                            unfocusedContainerColor = InputBg
                        )
                    )
                    OutlinedTextField(
                        value = editRemark,
                        onValueChange = { editRemark = it },
                        label = { Text("备注") },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(10.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = MaterialTheme.colorScheme.primary,
                            unfocusedBorderColor = BorderColor,
                            focusedContainerColor = InputBg,
                            unfocusedContainerColor = InputBg
                        )
                    )
                }
            },
            confirmButton = {
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    TextButton(
                        onClick = {
                            billViewModel.deleteBill(editBill!!.id) {
                                showEditDialog = false
                                dataViewModel.refreshAccounts()
                            }
                        },
                        colors = ButtonDefaults.textButtonColors(contentColor = ExpenseColor)
                    ) {
                        Text("删除", fontWeight = FontWeight.SemiBold)
                    }
                    Button(
                        onClick = {
                            val amount = editAmount.toDoubleOrNull()
                            if (amount != null) {
                                billViewModel.updateBill(
                                    editBill!!.id,
                                    BillUpdate(amount = amount, remark = editRemark)
                                ) {
                                    showEditDialog = false
                                    dataViewModel.refreshAccounts()
                                }
                            }
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary)
                    ) {
                        Text("保存")
                    }
                }
            }
        )
    }
}
