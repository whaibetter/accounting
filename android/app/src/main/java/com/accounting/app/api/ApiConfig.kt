package com.accounting.app.api

object ApiConfig {
    enum class Environment {
        LOCAL,
        REMOTE
    }

    var currentEnvironment = Environment.REMOTE

    private const val LOCAL_URL = "http://10.0.2.2:8000/api/v1/"
    private const val REMOTE_URL = "http://117.72.196.45:8000/api/v1/"

    val baseUrl: String
        get() = when (currentEnvironment) {
            Environment.LOCAL -> LOCAL_URL
            Environment.REMOTE -> REMOTE_URL
        }

    fun setLocal() {
        currentEnvironment = Environment.LOCAL
    }

    fun setRemote() {
        currentEnvironment = Environment.REMOTE
    }

    fun isLocal(): Boolean = currentEnvironment == Environment.LOCAL
}
