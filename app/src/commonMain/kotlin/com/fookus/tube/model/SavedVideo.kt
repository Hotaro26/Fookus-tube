package com.fookus.tube.model

import kotlinx.serialization.Serializable

@Serializable
data class SavedVideo(
    val url: String,
    val title: String,
    val uploader: String,
    val thumbUrl: String,
    val localUri: String? = null
)
