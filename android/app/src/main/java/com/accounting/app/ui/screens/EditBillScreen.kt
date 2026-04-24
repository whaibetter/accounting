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
import com.accounting.app.api.Bill
import com.accounting.app.api.BillUpdate
import com.accounting.app.ui.theme.AppColors
import com.accounting.app.viewmodel.BillViewModel
import com.accounting.app.viewmodel.DataViewModel

@Composable
fun EditBillScreen(billId: Int, onBack: () -> Unit) {
    val billViewModel: BillViewModel = viewModel()
    val dataViewModel: DataViewModel = viewModel()
    val bills by billViewModel.bills.collectAsState()

    var bill by remember { mutableStateOf<Bill?>(null) }
    var editAmount by remember { mutableStateOf("") }
    var editRemark by remember { mutableStateOf("") }
    var loading by remember { mutableStateOf(true) }

    LaunchedEffect(Unit) {
        dataViewModel.loadAll()
        billViewModel.loadBills(page = 1, size = 1000)
    }

    LaunchedEffect(bills) {
        val found = bills.find { it.id == billId }
        if (found != null && bill == null) {
            bill = found
            editAmount = found.amount.toString()
            editRemark = found.remark
            loading = false
        }
    }

    if (loading) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator(color = MaterialTheme.colorScheme.primary)
        }
        return
    }

    val currentBill = bill ?: return

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 20.dp)
            .verticalScroll(rememberScrollState())
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 16.dp, bottom = 24.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = onBack) {
                Text("‹", fontSize = 20.sp, color = MaterialTheme.colorScheme.onBackground)
            }
            Text(
                "编辑账单",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onBackground
            )
            Spacer(modifier = Modifier.width(36.dp))
        }

        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = AppColors.cardBg)
        ) {
            Column(modifier = Modifier.padding(20.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .clip(RoundedCornerShape(12.dp))
                            .background(AppColors.inputBg),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(getCategoryIcon(currentBill.category_id), fontSize = 20.sp)
                    }
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text(
                            currentBill.category_name,
                            fontSize = 15.sp,
                            fontWeight = FontWeight.Medium,
                            color = MaterialTheme.colorScheme.onBackground
                        )
                        Text(
                            currentBill.account_name,
                            fontSize = 12.sp,
                            color = AppColors.textMuted
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        Text("金额", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = editAmount,
            onValueChange = { editAmount = it },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(10.dp),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = MaterialTheme.colorScheme.primary,
                unfocusedBorderColor = AppColors.borderColor,
                focusedContainerColor = AppColors.inputBg,
                unfocusedContainerColor = AppColors.inputBg
            )
        )

        Spacer(modifier = Modifier.height(20.dp))

        Text("备注", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = editRemark,
            onValueChange = { editRemark = it },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(10.dp),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = MaterialTheme.colorScheme.primary,
                unfocusedBorderColor = AppColors.borderColor,
                focusedContainerColor = AppColors.inputBg,
                unfocusedContainerColor = AppColors.inputBg
            )
        )

        Spacer(modifier = Modifier.height(28.dp))

        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            OutlinedButton(
                onClick = {
                    billViewModel.deleteBill(billId) {
                        dataViewModel.refreshAccounts()
                        onBack()
                    }
                },
                modifier = Modifier
                    .weight(1f)
                    .height(52.dp),
                shape = RoundedCornerShape(10.dp),
                colors = ButtonDefaults.outlinedButtonColors(
                    containerColor = AppColors.expenseBgColor,
                    contentColor = AppColors.expenseColor
                )
            ) {
                Text("删除", fontWeight = FontWeight.SemiBold)
            }

            Button(
                onClick = {
                    val amountVal = editAmount.toDoubleOrNull()
                    if (amountVal != null) {
                        billViewModel.updateBill(
                            billId,
                            BillUpdate(amount = amountVal, remark = editRemark)
                        ) {
                            dataViewModel.refreshAccounts()
                            onBack()
                        }
                    }
                },
                modifier = Modifier
                    .weight(2f)
                    .height(52.dp),
                shape = RoundedCornerShape(10.dp),
                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary)
            ) {
                Text("保存", fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
            }
        }

        Spacer(modifier = Modifier.height(20.dp))
    }
}

