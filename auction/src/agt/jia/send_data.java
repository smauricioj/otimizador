// Internal action code for project auction

package jia;

import jason.asSemantics.*;
import jason.asSyntax.*;
import java.io.*;

@SuppressWarnings("serial")	
public class send_data extends DefaultInternalAction {
	
	BufferedWriter out = null;
	
	public send_data() {
		try {
			out = new BufferedWriter(new FileWriter(System.getProperty("user.dir")+"\\tmp\\data.csv", true));
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

    @Override
    public Object execute(TransitionSystem ts, Unifier un, Term[] args) throws Exception {
        // execute the internal action       
        out.write(args[0]+","+args[1]+"\n");        
        return true;
    }
    
    @Override
    public void destroy() throws Exception {
    	out.close();
    }
}
