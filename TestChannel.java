import org.schabi.newpipe.extractor.channel.ChannelInfo;
import java.lang.reflect.Method;
public class TestChannel {
    public static void main(String[] args) {
        for(Method m : ChannelInfo.class.getMethods()) {
            System.out.println(m.getName());
        }
    }
}
