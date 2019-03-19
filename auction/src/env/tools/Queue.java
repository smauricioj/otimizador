// CArtAgO artifact code for project auction

package tools;

import cartago.Artifact;
import cartago.OPERATION;
import cartago.INTERNAL_OPERATION;
import cartago.ObsProperty;

public class Queue extends Artifact {
	
	void init() {
		defineObsProperty("next", 0);
		execInternalOp("initial_inc");
	}

	@OPERATION
	void inc() {
		ObsProperty prop = getObsProperty("next");		
		prop.updateValue(prop.intValue()+1);
	}
	
	@INTERNAL_OPERATION
	void initial_inc() {
		await_time(50);
		inc();
	}
}
