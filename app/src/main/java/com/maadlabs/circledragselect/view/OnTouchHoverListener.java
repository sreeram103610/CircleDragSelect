package com.maadlabs.circledragselect.view;

import android.view.View;
import android.widget.AdapterView;

public abstract class OnTouchHoverListener {

    public abstract void onHover(AdapterView<?> parent, View v, int position);
}