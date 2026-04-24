package com.accounting.app.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.painterResource
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.accounting.app.ui.screens.*
import com.accounting.app.ui.theme.AppColors
import com.accounting.app.viewmodel.ThemeMode

sealed class Screen(val route: String) {
    data object Login : Screen("login")
    data object Home : Screen("home")
    data object Bills : Screen("bills")
    data object AddBill : Screen("add_bill")
    data object EditBill : Screen("edit_bill/{billId}") {
        fun createRoute(billId: Int) = "edit_bill/$billId"
    }
    data object Stats : Screen("stats")
    data object Accounts : Screen("accounts")
    data object Settings : Screen("settings")
    data object AiAccounting : Screen("ai_accounting")
    data object BalanceTrend : Screen("balance_trend")
}

data class BottomNavItem(
    val screen: Screen,
    val label: String,
    val icon: Int
)

@Composable
fun AppNavigation(
    isAuthenticated: Boolean,
    onLogout: () -> Unit,
    onThemeChange: (ThemeMode) -> Unit,
    currentThemeMode: ThemeMode
) {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination

    val bottomItems = listOf(
        BottomNavItem(Screen.Home, "首页", android.R.drawable.ic_menu_myplaces),
        BottomNavItem(Screen.Bills, "账单", android.R.drawable.ic_menu_agenda),
        BottomNavItem(Screen.AddBill, "记账", android.R.drawable.ic_menu_add),
        BottomNavItem(Screen.Stats, "统计", android.R.drawable.ic_menu_sort_by_size),
        BottomNavItem(Screen.Accounts, "账户", android.R.drawable.ic_menu_manage),
    )

    val bottomRoutes = bottomItems.map { it.screen.route }.toSet()
    val currentRoute = currentDestination?.route
    val showBottomBar = isAuthenticated && currentRoute != null && currentRoute in bottomRoutes

    val startDestination = if (isAuthenticated) Screen.Home.route else Screen.Login.route

    Scaffold(
        bottomBar = {
            if (showBottomBar) {
                NavigationBar(
                    containerColor = AppColors.navBarBg,
                    contentColor = AppColors.navBarActive
                ) {
                    bottomItems.forEach { item ->
                        val isSelected = currentRoute == item.screen.route
                        NavigationBarItem(
                            icon = {
                                Icon(
                                    painter = painterResource(id = item.icon),
                                    contentDescription = item.label,
                                    tint = if (isSelected) AppColors.navBarActive else AppColors.navBarInactive
                                )
                            },
                            label = {
                                Text(
                                    item.label,
                                    color = if (isSelected) AppColors.navBarActive else AppColors.navBarInactive
                                )
                            },
                            selected = isSelected,
                            onClick = {
                                navController.navigate(item.screen.route) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            },
                            colors = NavigationBarItemDefaults.colors(
                                indicatorColor = androidx.compose.ui.graphics.Color.Transparent
                            )
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = startDestination,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.Login.route) {
                LoginScreen(
                    onLoginSuccess = {
                        navController.navigate(Screen.Home.route) {
                            popUpTo(Screen.Login.route) { inclusive = true }
                        }
                    }
                )
            }
            composable(Screen.Home.route) {
                HomeScreen(
                    onNavigateToBills = { navController.navigate(Screen.Bills.route) },
                    onNavigateToAdd = { navController.navigate(Screen.AddBill.route) },
                    onNavigateToSettings = { navController.navigate(Screen.Settings.route) },
                    onNavigateToAi = { navController.navigate(Screen.AiAccounting.route) },
                    onLogout = onLogout
                )
            }
            composable(Screen.Bills.route) {
                BillsScreen(
                    onNavigateToAdd = { navController.navigate(Screen.AddBill.route) },
                    onNavigateToEdit = { billId -> navController.navigate(Screen.EditBill.createRoute(billId)) }
                )
            }
            composable(Screen.AddBill.route) {
                AddBillScreen(onBack = { navController.popBackStack() })
            }
            composable(
                route = Screen.EditBill.route,
                arguments = listOf(navArgument("billId") { type = NavType.IntType })
            ) { backStackEntry ->
                val billId = backStackEntry.arguments?.getInt("billId") ?: return@composable
                EditBillScreen(billId = billId, onBack = { navController.popBackStack() })
            }
            composable(Screen.Stats.route) {
                StatsScreen(
                    onNavigateToBalanceTrend = { navController.navigate(Screen.BalanceTrend.route) }
                )
            }
            composable(Screen.Accounts.route) {
                AccountsScreen(
                    onNavigateToSettings = { navController.navigate(Screen.Settings.route) }
                )
            }
            composable(Screen.Settings.route) {
                SettingsScreen(
                    currentThemeMode = currentThemeMode,
                    onThemeChange = onThemeChange,
                    onBack = { navController.popBackStack() }
                )
            }
            composable(Screen.AiAccounting.route) {
                AiAccountingScreen(onBack = { navController.popBackStack() })
            }
            composable(Screen.BalanceTrend.route) {
                BalanceTrendScreen(onBack = { navController.popBackStack() })
            }
        }
    }
}
