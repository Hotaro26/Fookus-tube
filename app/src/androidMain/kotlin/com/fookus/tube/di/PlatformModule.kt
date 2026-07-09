package com.fookus.tube.di

import org.koin.core.module.Module
import org.koin.dsl.module
import com.fookus.tube.util.PlatformBridge
import com.fookus.tube.util.AndroidPlatformBridge

actual fun platformModule(): Module = module {
    single<PlatformBridge> { AndroidPlatformBridge(get()) }
}
