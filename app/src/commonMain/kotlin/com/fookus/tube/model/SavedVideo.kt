package com.fookus.tube.model

import kotlinx.serialization.Serializable

@Serializable
data class SavedVideo(
    val url: String,
    val title: String,
    val uploader: String,
    val thumbUrl: String,
    val localUri: String? = null,
    val uploaderAvatarUrl: String? = null,
    val localThumbUri: String? = null,
    val localAvatarUri: String? = null
)

@Serializable
data class OfflinePreview(
    val title: String,
    val author: String,
    val thumbUrl: String,
    val maxResolution: String,
    val availableQualities: List<String>
)
