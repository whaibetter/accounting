package com.accounting.app.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
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
import com.accounting.app.api.BillCreate
import com.accounting.app.ui.theme.AppColors
import com.accounting.app.viewmodel.BillViewModel
import com.accounting.app.viewmodel.DataViewModel
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun AddBillScreen(onBack: () -> Unit) {
    val dataViewModel: DataViewModel = viewModel()
    val billViewModel: BillViewModel = viewModel()

    val accounts by dataViewModel.accounts.collectAsState()
    val expenseCategories by dataViewModel.expenseCategories.collectAsState()
    val incomeCategories by dataViewModel.incomeCategories.collectAsState()
    val tags by dataViewModel.tags.collectAsState()

    var billType by remember { mutableIntStateOf(1) }
    var amount by remember { mutableStateOf("") }
    var selectedCategoryId by remember { mutableIntStateOf(0) }
    var selectedAccountId by remember { mutableIntStateOf(0) }
    var billDate by remember { mutableStateOf(SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(Date())) }
    var remark by remember { mutableStateOf("") }
    var selectedTagIds by remember { mutableStateOf<List<Int>>(emptyList()) }

    var showDatePicker by remember { mutableStateOf(false) }
    var showToast by remember { mutableStateOf("") }

    LaunchedEffect(Unit) {
        dataViewModel.loadAll()
    }

    LaunchedEffect(accounts) {
        if (selectedAccountId == 0 && accounts.isNotEmpty()) {
            selectedAccountId = accounts[0].id
        }
    }

    val currentCategories = if (billType == 1) expenseCategories else incomeCategories

    LaunchedEffect(currentCategories) {
        if (selectedCategoryId == 0 && currentCategories.isNotEmpty()) {
            val first = currentCategories[0]
            selectedCategoryId = first.children.firstOrNull()?.id ?: first.id
        }
    }

    LaunchedEffect(billType) {
        selectedCategoryId = 0
    }

    val canSubmit = amount.toDoubleOrNull()?.let { it > 0 } == true &&
            selectedCategoryId > 0 && selectedAccountId > 0

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
                Text("✕", fontSize = 16.sp, color = MaterialTheme.colorScheme.onBackground)
            }
            Text(
                "记一笔",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onBackground
            )
            Spacer(modifier = Modifier.width(36.dp))
        }

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            listOf("支出" to 1, "收入" to 2).forEach { (label, type) ->
                OutlinedButton(
                    onClick = { billType = type },
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(10.dp),
                    colors = ButtonDefaults.outlinedButtonColors(
                        containerColor = when {
                            billType == type && type == 1 -> AppColors.expenseBgColor
                            billType == type && type == 2 -> AppColors.incomeBgColor
                            else -> AppColors.cardBg
                        },
                        contentColor = when {
                            billType == type && type == 1 -> AppColors.expenseColor
                            billType == type && type == 2 -> AppColors.incomeColor
                            else -> MaterialTheme.colorScheme.onSurfaceVariant
                        }
                    ),
                    border = BorderStroke(1.dp, when {
                        billType == type && type == 1 -> AppColors.expenseColor
                        billType == type && type == 2 -> AppColors.incomeColor
                        else -> AppColors.borderColor
                    })
                ) {
                    Text(label, fontWeight = FontWeight.SemiBold)
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = AppColors.cardBg)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("¥", fontSize = 28.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Spacer(modifier = Modifier.width(8.dp))
                OutlinedTextField(
                    value = amount,
                    onValueChange = { amount = it },
                    placeholder = { Text("0.00", fontSize = 36.sp, fontWeight = FontWeight.ExtraBold, color = AppColors.textMuted) },
                    modifier = Modifier.weight(1f),
                    textStyle = LocalTextStyle.current.copy(
                        fontSize = 36.sp,
                        fontWeight = FontWeight.ExtraBold,
                        color = MaterialTheme.colorScheme.onBackground
                    ),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = Color.Transparent,
                        unfocusedBorderColor = Color.Transparent,
                        focusedContainerColor = Color.Transparent,
                        unfocusedContainerColor = Color.Transparent,
                        cursorColor = MaterialTheme.colorScheme.primary
                    )
                )
            }
        }

        Spacer(modifier = Modifier.height(28.dp))

        Text("分类", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(modifier = Modifier.height(8.dp))

        FlowRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            currentCategories.forEach { cat ->
                val isSelected = selectedCategoryId == cat.id || cat.children.any { it.id == selectedCategoryId }
                Column(
                    modifier = Modifier
                        .width(64.dp)
                        .clip(RoundedCornerShape(10.dp))
                        .background(if (isSelected) AppColors.primaryBgColor else AppColors.cardBg)
                        .border(
                            1.dp,
                            if (isSelected) MaterialTheme.colorScheme.primary else AppColors.borderColor,
                            RoundedCornerShape(10.dp)
                        )
                        .clickable {
                            selectedCategoryId = cat.children.firstOrNull()?.id ?: cat.id
                        }
                        .padding(vertical = 10.dp, horizontal = 4.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(getCategoryIcon(cat.id), fontSize = 22.sp)
                    Text(
                        cat.name,
                        fontSize = 11.sp,
                        color = if (isSelected) MaterialTheme.colorScheme.secondary else MaterialTheme.colorScheme.onSurfaceVariant,
                        maxLines = 1
                    )
                }
            }
        }

        val selectedParent = currentCategories.find {
            it.id == selectedCategoryId || it.children.any { c -> c.id == selectedCategoryId }
        }
        val subCategories = selectedParent?.children ?: emptyList()

        if (subCategories.isNotEmpty()) {
            Spacer(modifier = Modifier.height(16.dp))
            Text("子分类", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Spacer(modifier = Modifier.height(8.dp))
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                subCategories.forEach { sub ->
                    val isSelected = selectedCategoryId == sub.id
                    OutlinedButton(
                        onClick = { selectedCategoryId = sub.id },
                        shape = RoundedCornerShape(10.dp),
                        colors = ButtonDefaults.outlinedButtonColors(
                            containerColor = if (isSelected) AppColors.primaryBgColor else AppColors.cardBg,
                            contentColor = if (isSelected) MaterialTheme.colorScheme.secondary else MaterialTheme.colorScheme.onSurfaceVariant
                        ),
                        border = BorderStroke(1.dp, if (isSelected) MaterialTheme.colorScheme.primary else AppColors.borderColor),
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 8.dp)
                    ) {
                        Text(sub.name, fontSize = 12.sp)
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        Text("账户", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(modifier = Modifier.height(8.dp))
        FlowRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            accounts.forEach { acc ->
                val isSelected = selectedAccountId == acc.id
                OutlinedButton(
                    onClick = { selectedAccountId = acc.id },
                    shape = RoundedCornerShape(20.dp),
                    colors = ButtonDefaults.outlinedButtonColors(
                        containerColor = if (isSelected) AppColors.primaryBgColor else AppColors.cardBg,
                        contentColor = if (isSelected) MaterialTheme.colorScheme.secondary else MaterialTheme.colorScheme.onSurfaceVariant
                    ),
                    border = BorderStroke(1.dp, if (isSelected) MaterialTheme.colorScheme.primary else AppColors.borderColor),
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp)
                ) {
                    Text(acc.name, fontSize = 13.sp)
                }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        Text("日期", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedButton(
            onClick = { showDatePicker = true },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(10.dp),
            colors = ButtonDefaults.outlinedButtonColors(
                containerColor = AppColors.inputBg,
                contentColor = MaterialTheme.colorScheme.onBackground
            ),
            border = BorderStroke(1.dp, AppColors.borderColor)
        ) {
            Text(billDate)
        }

        if (showDatePicker) {
            val datePickerState = rememberDatePickerState(
                initialSelectedDateMillis = System.currentTimeMillis()
            )
            DatePickerDialog(
                onDismissRequest = { showDatePicker = false },
                confirmButton = {
                    TextButton(onClick = {
                        datePickerState.selectedDateMillis?.let { millis ->
                            val sdf = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
                            billDate = sdf.format(Date(millis))
                        }
                        showDatePicker = false
                    }) { Text("确定") }
                },
                dismissButton = {
                    TextButton(onClick = { showDatePicker = false }) { Text("取消") }
                }
            ) {
                DatePicker(state = datePickerState)
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        Text("备注", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = remark,
            onValueChange = { remark = it },
            placeholder = { Text("添加备注...", color = AppColors.textMuted) },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(10.dp),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = MaterialTheme.colorScheme.primary,
                unfocusedBorderColor = AppColors.borderColor,
                focusedContainerColor = AppColors.inputBg,
                unfocusedContainerColor = AppColors.inputBg
            )
        )

        if (tags.isNotEmpty()) {
            Spacer(modifier = Modifier.height(20.dp))
            Text("标签", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Spacer(modifier = Modifier.height(8.dp))
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                tags.forEach { tag ->
                    val isSelected = selectedTagIds.contains(tag.id)
                    OutlinedButton(
                        onClick = {
                            selectedTagIds = if (isSelected) {
                                selectedTagIds.filter { it != tag.id }
                            } else {
                                selectedTagIds + tag.id
                            }
                        },
                        shape = RoundedCornerShape(20.dp),
                        colors = ButtonDefaults.outlinedButtonColors(
                            containerColor = if (isSelected) AppColors.primaryBgColor else AppColors.cardBg,
                            contentColor = if (isSelected) MaterialTheme.colorScheme.secondary else MaterialTheme.colorScheme.onSurfaceVariant
                        ),
                        border = BorderStroke(1.dp, if (isSelected) MaterialTheme.colorScheme.primary else AppColors.borderColor),
                        contentPadding = PaddingValues(horizontal = 14.dp, vertical = 6.dp)
                    ) {
                        Text(tag.name, fontSize = 13.sp)
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(28.dp))

        Button(
            onClick = {
                val amountVal = amount.toDoubleOrNull() ?: 0.0
                if (amountVal <= 0 || selectedCategoryId == 0 || selectedAccountId == 0) return@Button

                billViewModel.createBill(
                    BillCreate(
                        account_id = selectedAccountId,
                        category_id = selectedCategoryId,
                        type = billType,
                        amount = amountVal,
                        bill_date = billDate,
                        remark = remark,
                        tag_ids = selectedTagIds
                    ),
                    onSuccess = {
                        dataViewModel.refreshAccounts()
                        onBack()
                    },
                    onError = { showToast = it }
                )
            },
            enabled = canSubmit,
            modifier = Modifier
                .fillMaxWidth()
                .height(52.dp),
            shape = RoundedCornerShape(10.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = MaterialTheme.colorScheme.primary,
                disabledContainerColor = MaterialTheme.colorScheme.primary.copy(alpha = 0.4f)
            )
        ) {
            Text("保存", fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
        }

        Spacer(modifier = Modifier.height(20.dp))
    }

    if (showToast.isNotEmpty()) {
        LaunchedEffect(showToast) {
            kotlinx.coroutines.delay(2500)
            showToast = ""
        }
        Snackbar(
            modifier = Modifier.padding(16.dp),
            containerColor = AppColors.expenseColor,
            contentColor = MaterialTheme.colorScheme.onPrimary
        ) {
            Text(showToast)
        }
    }
}

