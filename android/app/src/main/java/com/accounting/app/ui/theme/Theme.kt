package com.accounting.app.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

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

val IncomeColor = Color(0xFF34D399)
val ExpenseColor = Color(0xFFF87171)
val IncomeBgColor = Color(0x1F34D399)
val ExpenseBgColor = Color(0x1FF87171)
val PrimaryBgColor = Color(0x1F6366F1)
val TextMuted = Color(0xFF55556A)
val BorderColor = Color(0xFF2A2A3A)
val CardBg = Color(0xFF1A1A24)
val InputBg = Color(0xFF16161F)

@Composable
fun AccountingTheme(
    content: @Composable () -> Unit
) {
    val colorScheme = DarkColorScheme
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = Color(0xFF0F0F13).toArgb()
            window.navigationBarColor = Color(0xFF0F0F13).toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = false
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        content = content
    )
}
