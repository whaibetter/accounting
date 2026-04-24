package com.accounting.app.api

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "accounting_prefs")

object ApiClient {

    private val TOKEN_KEY = stringPreferencesKey("access_token")

    @Volatile
    private var token: String = ""
    private var dataStoreRef: DataStore<Preferences>? = null

    suspend fun init(context: Context) {
        dataStoreRef = context.dataStore
        token = context.dataStore.data.map { it[TOKEN_KEY] ?: "" }.first()
    }

    suspend fun saveToken(newToken: String) {
        token = newToken
        dataStoreRef?.edit { it[TOKEN_KEY] = newToken }
    }

    suspend fun clearToken() {
        token = ""
        dataStoreRef?.edit { it.remove(TOKEN_KEY) }
    }

    fun getToken(): String = token

    private val authInterceptor = Interceptor { chain ->
        val request = if (token.isNotEmpty()) {
            chain.request().newBuilder()
                .addHeader("Authorization", "Bearer $token")
                .build()
        } else {
            chain.request()
        }
        chain.proceed(request)
    }

    private val client: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .retryOnConnectionFailure(true)
            .build()
    }

    val api: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(ApiConfig.baseUrl)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}
