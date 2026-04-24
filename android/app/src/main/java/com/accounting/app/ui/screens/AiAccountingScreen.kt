package com.accounting.app.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.accounting.app.api.ApiClient
import com.accounting.app.ui.theme.AppColors
import kotlinx.coroutines.launch
import org.json.JSONObject

@Composable
fun AiAccountingScreen(
    onBack: () -> Unit = {}
) {
    var inputText by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf("") }
    var result by remember { mutableStateOf("") }
    var isConfigured by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()

    LaunchedEffect(Unit) {
        try {
            val resp = ApiClient.api.getLlmConfig()
            isConfigured = resp.api_key?.isNotEmpty() == true
        } catch (_: Exception) {
            isConfigured = false
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
                .padding(top = 16.dp, bottom = 24.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            TextButton(onClick = onBack) {
                Text("← 返回", color = MaterialTheme.colorScheme.primary)
            }
            Spacer(modifier = Modifier.weight(1f))
            Text(
                "AI 记账",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onBackground
            )
            Spacer(modifier = Modifier.weight(1f))
            Spacer(modifier = Modifier.width(48.dp))
        }

        if (!isConfigured) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = AppColors.expenseBgColor)
            ) {
                Text(
                    "⚠ AI 模型未配置，请先在网页端设置 LLM 配置",
                    modifier = Modifier.padding(16.dp),
                    fontSize = 14.sp,
                    color = AppColors.expenseColor
                )
            }
            Spacer(modifier = Modifier.height(16.dp))
        }

        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            colors = CardDefaults.cardColors(containerColor = AppColors.cardBg)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    "描述你的消费",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.onBackground
                )
                Spacer(modifier = Modifier.height(8.dp))

                OutlinedTextField(
                    value = inputText,
                    onValueChange = { inputText = it },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(120.dp),
                    placeholder = { Text("例如：今天午饭花了25元", color = AppColors.textMuted) },
                    shape = RoundedCornerShape(10.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        unfocusedContainerColor = AppColors.inputBg,
                        focusedContainerColor = AppColors.inputBg,
                        unfocusedBorderColor = AppColors.borderColor,
                        focusedBorderColor = MaterialTheme.colorScheme.primary
                    )
                )

                Spacer(modifier = Modifier.height(12.dp))

                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    listOf("午饭25元", "打车去公司30", "超市买菜86.5").forEach { example ->
                        OutlinedButton(
                            onClick = { inputText = example },
                            shape = RoundedCornerShape(8.dp),
                            colors = ButtonDefaults.outlinedButtonColors(
                                containerColor = AppColors.primaryBgColor,
                                contentColor = MaterialTheme.colorScheme.primary
                            )
                        ) {
                            Text(example, fontSize = 12.sp)
                        }
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                Button(
                    onClick = {
                        if (inputText.isBlank()) return@Button
                        isLoading = true
                        error = ""
                        result = ""
                        scope.launch {
                            try {
                                val resp = ApiClient.api.aiAccounting(mapOf("text" to inputText))
                                result = resp.toString()
                            } catch (e: Exception) {
                                error = e.message ?: "解析失败"
                            } finally {
                                isLoading = false
                            }
                        }
                    },
                    enabled = !isLoading && inputText.isNotBlank() && isConfigured,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(48.dp),
                    shape = RoundedCornerShape(10.dp)
                ) {
                    if (isLoading) {
                        Text("解析中...", fontSize = 15.sp)
                    } else {
                        Text("🤖 AI 解析", fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
                    }
                }
            }
        }

        if (error.isNotEmpty()) {
            Spacer(modifier = Modifier.height(12.dp))
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = AppColors.expenseBgColor)
            ) {
                Text(
                    error,
                    modifier = Modifier.padding(16.dp),
                    fontSize = 14.sp,
                    color = AppColors.expenseColor
                )
            }
        }

        if (result.isNotEmpty()) {
            Spacer(modifier = Modifier.height(12.dp))
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = AppColors.cardBg)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        "解析结果",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = MaterialTheme.colorScheme.onBackground
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        result,
                        fontSize = 13.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}
