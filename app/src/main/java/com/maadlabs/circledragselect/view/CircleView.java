package com.maadlabs.circledragselect.view;


import android.content.Context;
import android.content.res.TypedArray;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Rect;
import android.util.AttributeSet;
import android.util.Log;
import android.view.View;

import com.maadlabs.circledragselect.R;

public class CircleView extends View {

    private static final int TWENTY = 20;
    float mPointX, mPointY, mRadius;
    private Paint mCirclePaint;
    private String mText;
    private Boolean mShowText;
    private boolean mCursor = false, mMoveFlag = false;
    private Paint mTextPaint;
    private int mCircleColor = -1;
    private Rect mTextBounds;

    public CircleView(Context context, AttributeSet attrs) {
        super(context, attrs);

        TypedArray typedArray = context.getTheme().obtainStyledAttributes(attrs, R.styleable.CircleView, 0, 0);

        try {
            mText = typedArray.getString(R.styleable.CircleView_text);
            mShowText = typedArray.getBoolean(R.styleable.CircleView_showText, false);
            mCircleColor = typedArray.getInteger(R.styleable.CircleView_color, -1);
        } finally {
            typedArray.recycle();
        }
        init();
    }

    private void init() {

        mCirclePaint = new Paint(Paint.ANTI_ALIAS_FLAG);

        mTextPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        mTextPaint.setColor(Color.BLACK);
        mTextPaint.setTextSize(pixelsToSp(getContext(), TWENTY));

        if(mShowText) {
            setText(mText);
        }
        mTextBounds = new Rect();
    }

    public static float pixelsToSp(Context context, float sp) {
        float scaledDensity = context.getResources().getDisplayMetrics().scaledDensity;
        return sp * scaledDensity;
    }
    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        mPointX = getWidth()/2;
        mPointY = getHeight()/2;

        if(!mMoveFlag) {
            mRadius = getWidth()/4;
            if(mCircleColor == -1)
                mCirclePaint.setColor(Color.BLUE);
            else
                mCirclePaint.setColor(mCircleColor);

            mCirclePaint.setStyle(Paint.Style.FILL);
        }
        else
        {
            mRadius = getWidth()/2;
            mCirclePaint.setColor(Color.BLUE);
            mCirclePaint.setStyle(Paint.Style.STROKE);
            mCirclePaint.setStrokeWidth(7);

        }

        canvas.drawCircle(mPointX, mPointY, mRadius, mCirclePaint);

        if(mText != null) {
            Log.i("txt", mText);

            mTextPaint.getTextBounds(mText, 0, mText.length(), mTextBounds);

            canvas.drawText(mText, mPointX - mTextBounds.width()/2, mPointY + mTextBounds.height()/2, mTextPaint);
        }

        Log.i("px/py/r", mPointX + "/" + mPointY + "/" + mRadius);
    }



    @Override
    protected void onLayout(boolean changed, int left, int top, int right,
                            int bottom) {
        // TODO Auto-generated method stub
        super.onLayout(changed, left, top, right, bottom);
        Log.i("l/t/r/b", left + "/" + top + "/" + right + "/" + bottom);
    }

/*	@Override
	public boolean onTouchEvent(MotionEvent event) {
        
		int index = event.getActionIndex();
        int action = event.getAction();
        int pointerId = event.getPointerId(index);

        Animation animation = AnimationUtils.loadAnimation(getContext(), R.anim.border_zoom_in);
       
        switch(action) {
        
      		case MotionEvent.ACTION_DOWN:
      			Log.i("action", event.getRawX() + "/" + event.getX() + "/" + event.getXPrecision() + "/" + event.getRawY() + "/" + event.getY() + "/" + event.getYPrecision());
      	      	Log.i("action", "down");
      	      	mMoveFlag = true;
	      	    invalidate();

      	      	break;
      		
      		case MotionEvent.ACTION_MOVE:
      			int xOffset = getRight() - getLeft();
      			int yOffset = getBottom() - getTop();
      			
      			if(getParent() != null) {
      				
      				
      			}
      			layout((int) event.getRawX() - xOffset/2,(int)  event.getRawY() -200 - yOffset/2 ,(int)  event.getRawX() + xOffset/2,(int)  event.getRawY() -200 + yOffset/2);
      			Log.i("action", event.getRawX() + "/" + event.getX() + "/" + xOffset + "/" + event.getRawY() + "/" + event.getY() + "/" + yOffset);
      			break;
      			
      		case MotionEvent.ACTION_UP:
      			mMoveFlag = false;
      			invalidate();

      			Log.i("action", "up");
      			break;
      	}
		
		return true;
	} */

    @Override
    protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
        // TODO Auto-generated method stub
        //super.onMeasure(widthMeasureSpec, heightMeasureSpec);

        setMeasuredDimension(widthMeasureSpec, heightMeasureSpec);
        Log.i("cw/ch", MeasureSpec.getSize(widthMeasureSpec) + "/" + MeasureSpec.getSize(heightMeasureSpec));
    }

    public void setText(String text) {

        mText = text;

        invalidate();
        requestLayout();
    }

    public String getText() {

        return mText;
    }

    public void setMoveFlag(boolean flag) {

        mMoveFlag = flag;
    }
    public void setOption(Boolean flag) {

        mCursor = flag;
    }

    public int getCircleColor() {
        return mCircleColor;
    }

    public void setCircleColor(int mCircleColor) {
        this.mCircleColor = mCircleColor;
    }

    public class Holder {

        public CircleView circleView;
    }

}
