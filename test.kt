import org.schabi.newpipe.extractor.stream.AudioStream

fun main() {
    val clazz = AudioStream::class.java
    clazz.methods.forEach { println(it.name) }
}
