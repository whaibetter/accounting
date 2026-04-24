package com.accounting.app.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.accounting.app.api.ApiConfig
import com.accounting.app.ui.theme.AppColors
import com.accounting.app.viewmodel.ThemeMode

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    currentThemeMode: ThemeMode,
    onThemeChange: (ThemeMode) -> Unit,
    onBack: () -> Unit
) {
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
                "设置",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onBackground
            )
            Spacer(modifier = Modifier.weight(1f))
            Spacer(modifier = Modifier.width(48.dp))
        }

        Text(
            "服务器设置",
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
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    "API 服务器",
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.onBackground
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    "选择连接的服务器环境",
                    fontSize = 12.sp,
                    color = AppColors.textMuted
                )
                Spacer(modifier = Modifier.height(16.dp))

                ServerOptionItem(
                    label = "远程服务器",
                    description = "117.72.196.45 (生产环境)",
                    selected = ApiConfig.currentEnvironment == ApiConfig.Environment.REMOTE,
                    onClick = { ApiConfig.setRemote() }
                )
                Spacer(modifier = Modifier.height(8.dp))
                ServerOptionItem(
                    label = "本地服务器",
                    description = "10.0.2.2:8000 (开发调试)",
                    selected = ApiConfig.currentEnvironment == ApiConfig.Environment.LOCAL,
                    onClick = { ApiConfig.setLocal() }
                )
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        Text(
            "外观设置",
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
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    "主题模式",
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.onBackground
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    "选择应用的外观主题",
                    fontSize = 12.sp,
                    color = AppColors.textMuted
                )
                Spacer(modifier = Modifier.height(16.dp))

                ThemeOptionItem(
                    label = "跟随系统",
                    description = "根据系统设置自动切换",
                    selected = currentThemeMode == ThemeMode.SYSTEM,
                    onClick = { onThemeChange(ThemeMode.SYSTEM) }
                )
                Spacer(modifier = Modifier.height(8.dp))
                ThemeOptionItem(
                    label = "浅色模式",
                    description = "使用明亮的浅色界面",
                    selected = currentThemeMode == ThemeMode.LIGHT,
                    onClick = { onThemeChange(ThemeMode.LIGHT) }
                )
                Spacer(modifier = Modifier.height(8.dp))
                ThemeOptionItem(
                    label = "深色模式",
                    description = "使用暗色界面，减少视觉疲劳",
                    selected = currentThemeMode == ThemeMode.DARK,
                    onClick = { onThemeChange(ThemeMode.DARK) }
                )
            }
        }
    }
}

@Composable
private fun ServerOptionItem(
    label: String,
    description: String,
    selected: Boolean,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (selected) AppColors.primaryBgColor else AppColors.inputBg
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            RadioButton(
                selected = selected,
                onClick = onClick,
                colors = RadioButtonDefaults.colors(
                    selectedColor = MaterialTheme.colorScheme.primary,
                    unselectedColor = AppColors.textMuted
                )
            )
            Spacer(modifier = Modifier.width(8.dp))
            Column {
                Text(
                    label,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.onBackground
                )
                Text(
                    description,
                    fontSize = 12.sp,
                    color = AppColors.textMuted
                )
            }
        }
    }
}

@Composable
private fun ThemeOptionItem(
    label: String,
    description: String,
    selected: Boolean,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (selected) AppColors.primaryBgColor else AppColors.inputBg
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            RadioButton(
                selected = selected,
                onClick = onClick,
                colors = RadioButtonDefaults.colors(
                    selectedColor = MaterialTheme.colorScheme.primary,
                    unselectedColor = AppColors.textMuted
                )
            )
            Spacer(modifier = Modifier.width(8.dp))
            Column {
                Text(
                    label,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.onBackground
                )
                Text(
                    description,
                    fontSize = 12.sp,
                    color = AppColors.textMuted
                )
            }
        }
    }
}
