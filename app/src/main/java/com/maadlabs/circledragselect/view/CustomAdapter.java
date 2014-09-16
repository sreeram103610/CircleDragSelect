package com.maadlabs.circledragselect.view;

import java.util.ArrayList;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;

public abstract class CustomAdapter<T> extends ArrayAdapter<T>{

    Context context;
    int resource;
    public int myPosition;
    public ArrayList<T> values;
    protected View row;

    public CustomAdapter(Context context, int resource, ArrayList<T> objects)
    {
        super(context, resource, objects);
        this.context = context;
        this.resource = resource;
        this.values = objects;
    }

    public ArrayList<T> getValues()
    {
        return values;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {


        if(convertView == null)
        {
            LayoutInflater inflater = (LayoutInflater) context
                    .getSystemService(Context.LAYOUT_INFLATER_SERVICE);
            row = inflater.inflate(resource, parent, false);  // like a template to add values

            holderInitIf(row);
        }

        else
        {
            row = convertView;
            holderInitElse();
        }

        myPosition = position;
        setValues();

        return row;
    }

    public int getPosition()
    {
        return myPosition;
    }

    public abstract void holderInitIf(View row);

    public abstract void holderInitElse();

    public abstract void setValues();

    @Override
    public int getCount() {
        // TODO Auto-generated method stub
        return values.size();
    }

    @Override
    public T getItem(int position) {
        // TODO Auto-generated method stub
        return null;
    }

    @Override
    public long getItemId(int position) {
        // TODO Auto-generated method stub
        return 0;
    }

}
