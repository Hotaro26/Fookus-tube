import org.schabi.newpipe.extractor.channel.ChannelInfo
fun test() {
    println(ChannelInfo::class.java.methods.map { it.name }.joinToString("\n"))
}
