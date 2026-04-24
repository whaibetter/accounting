package com.accounting.app.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.accounting.app.api.Account
import com.accounting.app.ui.theme.AppColors
import com.accounting.app.viewmodel.AccountViewModel

val typeLabels = mapOf(1 to "现金", 2 to "银行卡", 3 to "信用卡", 4 to "支付宝", 5 to "微信", 6 to "其他")
val typeIcons = mapOf(1 to "💵", 2 to "🏦", 3 to "💳", 4 to "🔵", 5 to "💚", 6 to "📌")

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun AccountsScreen(
    onNavigateToSettings: () -> Unit = {}
) {
    val accountViewModel: AccountViewModel = viewModel()
    val accounts by accountViewModel.accounts.collectAsState()

    var newName by remember { mutableStateOf("") }
    var newType by remember { mutableIntStateOf(1) }
    var newBalance by remember { mutableStateOf("") }
    var showDeleteDialog by remember { mutableStateOf<Account?>(null) }

    LaunchedEffect(Unit) { accountViewModel.loadAccounts() }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 20.dp)
            .verticalScroll(rememberScrollState())
            .padding(top = 16.dp, bottom = 80.dp)
    ) {
        Text(
            "账户",
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onBackground
        )

        Spacer(modifier = Modifier.height(20.dp))

        val totalBalance = accounts.sumOf { it.balance }
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = AppColors.overviewCardBg)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(28.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text("总资产", fontSize = 13.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    "¥${formatMoney(totalBalance)}",
                    fontSize = 32.sp,
                    fontWeight = FontWeight.ExtraBold,
                    color = if (totalBalance >= 0) AppColors.incomeColor else AppColors.expenseColor,
                    letterSpacing = (-1).sp
                )
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        if (accounts.isNotEmpty()) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                accounts.forEach { acc ->
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(16.dp),
                        colors = CardDefaults.cardColors(containerColor = AppColors.cardBg)
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp)
                                .clickable { showDeleteDialog = acc },
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Box(
                                    modifier = Modifier
                                        .size(44.dp)
                                        .clip(RoundedCornerShape(12.dp))
                                        .background(AppColors.inputBg),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text(typeIcons[acc.type] ?: "💳", fontSize = 22.sp)
                                }
                                Spacer(modifier = Modifier.width(12.dp))
                                Column {
                                    Text(
                                        acc.name,
                                        fontSize = 15.sp,
                                        fontWeight = FontWeight.Medium,
                                        color = MaterialTheme.colorScheme.onBackground
                                    )
                                    Text(
                                        typeLabels[acc.type] ?: "其他",
                                        fontSize = 12.sp,
                                        color = AppColors.textMuted
                                    )
                                }
                            }
                            Text(
                                "¥${formatMoney(acc.balance)}",
                                fontSize = 17.sp,
                                fontWeight = FontWeight.Bold,
                                color = if (acc.balance >= 0) AppColors.incomeColor else AppColors.expenseColor
                            )
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(28.dp))

        Text(
            "添加账户",
            fontSize = 13.sp,
            fontWeight = FontWeight.SemiBold,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(modifier = Modifier.height(12.dp))

        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = AppColors.cardBg)
        ) {
            Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
                Text("账户名称", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurfaceVariant)
                OutlinedTextField(
                    value = newName,
                    onValueChange = { newName = it },
                    placeholder = { Text("如：招商银行储蓄卡", color = AppColors.textMuted) },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(10.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = MaterialTheme.colorScheme.primary,
                        unfocusedBorderColor = AppColors.borderColor,
                        focusedContainerColor = AppColors.inputBg,
                        unfocusedContainerColor = AppColors.inputBg
                    )
                )

                Text("账户类型", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurfaceVariant)
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    typeLabels.entries.forEach { (key, label) ->
                        val isSelected = newType == key
                        OutlinedButton(
                            onClick = { newType = key },
                            shape = RoundedCornerShape(10.dp),
                            colors = ButtonDefaults.outlinedButtonColors(
                                containerColor = if (isSelected) AppColors.primaryBgColor else AppColors.inputBg,
                                contentColor = if (isSelected) MaterialTheme.colorScheme.secondary else MaterialTheme.colorScheme.onSurfaceVariant
                            ),
                            border = BorderStroke(1.dp, if (isSelected) MaterialTheme.colorScheme.primary else AppColors.borderColor),
                            contentPadding = PaddingValues(horizontal = 12.dp, vertical = 10.dp)
                        ) {
                            Text("${typeIcons[key]} $label", fontSize = 13.sp)
                        }
                    }
                }

                Text("初始余额", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurfaceVariant)
                OutlinedTextField(
                    value = newBalance,
                    onValueChange = { newBalance = it },
                    placeholder = { Text("0.00", color = AppColors.textMuted) },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(10.dp),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = MaterialTheme.colorScheme.primary,
                        unfocusedBorderColor = AppColors.borderColor,
                        focusedContainerColor = AppColors.inputBg,
                        unfocusedContainerColor = AppColors.inputBg
                    )
                )

                Button(
                    onClick = {
                        if (newName.isNotEmpty()) {
                            accountViewModel.createAccount(
                                name = newName,
                                type = newType,
                                initialBalance = newBalance.toDoubleOrNull() ?: 0.0
                            )
                            newName = ""
                            newType = 1
                            newBalance = ""
                        }
                    },
                    enabled = newName.isNotEmpty(),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(52.dp),
                    shape = RoundedCornerShape(10.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary)
                ) {
                    Text("添加", fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
                }
            }
        }
    }

    showDeleteDialog?.let { account ->
        AlertDialog(
            onDismissRequest = { showDeleteDialog = null },
            title = { Text("删除账户") },
            text = { Text("确定要删除「${account.name}」吗？") },
            containerColor = AppColors.cardBg,
            confirmButton = {
                TextButton(
                    onClick = {
                        accountViewModel.deleteAccount(account.id)
                        showDeleteDialog = null
                    },
                    colors = ButtonDefaults.textButtonColors(contentColor = AppColors.expenseColor)
                ) {
                    Text("删除")
                }
            },
            dismissButton = {
                TextButton(onClick = { showDeleteDialog = null }) {
                    Text("取消")
                }
            }
        )
    }
}

