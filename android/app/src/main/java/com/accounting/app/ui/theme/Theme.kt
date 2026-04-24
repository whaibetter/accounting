package com.accounting.app.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat
import com.accounting.app.viewmodel.ThemeMode

private val DarkColorScheme = darkColorScheme(
    primary = Color(0xFF6366F1),
    onPrimary = Color.White,
    primaryContainer = Color(0xFF1E1E30),
    onPrimaryContainer = Color(0xFF818CF8),
    secondary = Color(0xFF818CF8),
    background = Color(0xFF0F0F13),
    onBackground = Color(0xFFE8E8ED),
    surface = Color(0xFF1A1A24),
    onSurface = Color(0xFFE8E8ED),
    surfaceVariant = Color(0xFF16161F),
    onSurfaceVariant = Color(0xFF8888A0),
    outline = Color(0xFF2A2A3A),
    error = Color(0xFFF87171),
    onError = Color.White,
)

private val LightColorScheme = lightColorScheme(
    primary = Color(0xFF4F46E5),
    onPrimary = Color.White,
    primaryContainer = Color(0xFFE0E7FF),
    onPrimaryContainer = Color(0xFF4338CA),
    secondary = Color(0xFF6366F1),
    background = Color(0xFFF8F9FC),
    onBackground = Color(0xFF1A1A2E),
    surface = Color(0xFFFFFFFF),
    onSurface = Color(0xFF1A1A2E),
    surfaceVariant = Color(0xFFF1F3F9),
    onSurfaceVariant = Color(0xFF6B7280),
    outline = Color(0xFFE5E7EB),
    error = Color(0xFFEF4444),
    onError = Color.White,
)

object AppColors {
    val incomeColor: Color @Composable get() = if (isDark()) Color(0xFF34D399) else Color(0xFF059669)
    val expenseColor: Color @Composable get() = if (isDark()) Color(0xFFF87171) else Color(0xFFDC2626)
    val incomeBgColor: Color @Composable get() = if (isDark()) Color(0x1F34D399) else Color(0x1F059669)
    val expenseBgColor: Color @Composable get() = if (isDark()) Color(0x1FF87171) else Color(0x1FDC2626)
    val primaryBgColor: Color @Composable get() = if (isDark()) Color(0x1F6366F1) else Color(0x1F4F46E5)
    val textMuted: Color @Composable get() = if (isDark()) Color(0xFF55556A) else Color(0xFF9CA3AF)
    val borderColor: Color @Composable get() = if (isDark()) Color(0xFF2A2A3A) else Color(0xFFE5E7EB)
    val cardBg: Color @Composable get() = if (isDark()) Color(0xFF1A1A24) else Color(0xFFFFFFFF)
    val inputBg: Color @Composable get() = if (isDark()) Color(0xFF16161F) else Color(0xFFF1F3F9)
    val navBarBg: Color @Composable get() = if (isDark()) Color(0xFF0F0F13) else Color(0xFFF8F9FC)
    val navBarActive: Color @Composable get() = if (isDark()) Color(0xFF818CF8) else Color(0xFF4F46E5)
    val navBarInactive: Color @Composable get() = if (isDark()) Color(0xFF55556A) else Color(0xFF9CA3AF)
    val overviewCardBg: Color @Composable get() = if (isDark()) Color(0xFF1E1E30) else Color(0xFFE0E7FF)
    val statusBarBg: Color @Composable get() = if (isDark()) Color(0xFF0F0F13) else Color(0xFFF8F9FC)
    val barColorHigh: Color @Composable get() = if (isDark()) Color(0xFFF87171) else Color(0xFFDC2626)
    val barColorMedium: Color @Composable get() = if (isDark()) Color(0xFFFB923C) else Color(0xFFEA580C)
    val barColorLow: Color @Composable get() = if (isDark()) Color(0xFFFACC15) else Color(0xFFCA8A04)
    val barColorDefault: Color @Composable get() = if (isDark()) Color(0xFF6366F1) else Color(0xFF4F46E5)
}

private var _isDarkTheme = true
val isDark: Boolean get() = _isDarkTheme

@Composable
private fun isDark(): Boolean = _isDarkTheme

@Composable
fun AccountingTheme(
    themeMode: ThemeMode = ThemeMode.SYSTEM,
    content: @Composable () -> Unit
) {
    val darkTheme = when (themeMode) {
        ThemeMode.DARK -> true
        ThemeMode.LIGHT -> false
        ThemeMode.SYSTEM -> isSystemInDarkTheme()
    }
    _isDarkTheme = darkTheme

    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            val statusBarColor = if (darkTheme) Color(0xFF0F0F13) else Color(0xFFF8F9FC)
            window.statusBarColor = statusBarColor.toArgb()
            window.navigationBarColor = statusBarColor.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        content = content
    )
}
