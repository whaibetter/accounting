package com.accounting.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.viewmodel.compose.viewModel
import com.accounting.app.api.ApiClient
import com.accounting.app.ui.navigation.AppNavigation
import com.accounting.app.ui.theme.AccountingTheme
import com.accounting.app.viewmodel.AuthViewModel
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : ComponentActivity() {
    
    private var isReady by mutableStateOf(false)
        private set

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        lifecycleScope.launch {
            ApiClient.init(this@MainActivity)
            withContext(Dispatchers.Main) {
                isReady = true
            }
        }
        
        setContent {
            AccountingTheme {
                if (isReady) {
                    val authViewModel: AuthViewModel = viewModel()
                    val isAuthenticated by authViewModel.isAuthenticated.collectAsState()
                    
                    AppNavigation(
                        isAuthenticated = isAuthenticated,
                        onLogout = { authViewModel.logout() }
                    )
                }
            }
        }
    }
}
