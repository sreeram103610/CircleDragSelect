package com.maadlabs.circledragselect.view;

import android.content.Context;
import android.content.res.Configuration;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Adapter;
import android.widget.AdapterView;

public class CirclesOptionView extends AdapterView<Adapter> {

	private static final int THREE = 3;
	private static final int ONE = 1;
	private static final int TWO = 2;
	private static final int ZERO = 0;
	String mText;
	Integer mNumOptions;
	Paint mTextPaint;
	Adapter mAdapter;
	private int mAnchorPosition[];
	private float mTextHeight, mCircleRadius;
	private Paint mCirclePaint;
	private int mLayoutOrientation;
	private float mOriginDist;
	private int mOptionLineValues[];
	public static final float F_INIT_VALUE = 0.5f;
	public static final float F_DEC_VALUE = 0.0833f;
	public static float[] circlePoints = { ZERO, 90, 90, 45 };
	public CircleView mCircleSelect;
	private OnTouchHoverListener mOnHoverListener;
	private Paint mLinePaint;
	private Line mCurrentChildLine;

	private enum Line {
		NONE, LEFT, RIGHT, TOP
	}

	public CirclesOptionView(Context context) {
		super(context);

	}

	public CirclesOptionView(Context context, AttributeSet attrs) {
		super(context, attrs);

		mLayoutOrientation = context.getResources().getConfiguration().orientation;
		mCircleSelect = new CircleView(context, null);
		init();
	}

	public CirclesOptionView(Context context, AttributeSet attrs, int style) {
		super(context, attrs, style);

		mLayoutOrientation = context.getResources().getConfiguration().orientation;
		init();
	}

	public void setOnItemHoverListener(OnTouchHoverListener onTouchHoverListener) {

		mOnHoverListener = onTouchHoverListener;
	}

	@Override
	protected void onDraw(Canvas canvas) {
		// TODO Auto-generated method stub
		super.onDraw(canvas);

		// lineDraw(canvas);
	}

	
	@Override
	protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {

		super.onMeasure(widthMeasureSpec, heightMeasureSpec);

		if (getCount() > ZERO) {
			int widthSpec, heightSpec;
			float f = F_INIT_VALUE - getCount() * F_DEC_VALUE;

			mOriginDist = F_INIT_VALUE - F_INIT_VALUE / 6;

			widthSpec = MeasureSpec.makeMeasureSpec((int) (getWidth() * f * 2),
					MeasureSpec.EXACTLY);
			heightSpec = MeasureSpec.makeMeasureSpec((int) (getWidth() * f * 2),
					MeasureSpec.EXACTLY);

			for (int i = ZERO; i < getCount(); i++) {

				View v = getChildAt(i);

				v.measure(widthSpec, heightSpec);
				Log.i("mw", v.getMeasuredHeight() + "/" + getChildCount());
			}

			widthSpec = MeasureSpec.makeMeasureSpec((int) (getWidth() * f),
					MeasureSpec.AT_MOST);
			heightSpec = MeasureSpec.makeMeasureSpec((int) (getWidth() * f),
					MeasureSpec.AT_MOST);

			mCircleSelect.measure(widthSpec, heightSpec);
			// setMeasuredDimension(MeasureSpec.getSize(widthMeasureSpec),
			// MeasureSpec.getSize(heightMeasureSpec));
		}
	}

	@Override
	public int getCount() {

		if (mAdapter == null)
			return ZERO;

		return mAdapter.getCount();
	}

	@Override
	protected void onLayout(boolean changed, int left, int top, int right,
			int bottom) {
		// TODO Auto-generated method stub

		super.onLayout(changed, left, top, right, bottom);
		if (getCount() > ZERO) {
			int centerX = ZERO, centerY = ZERO, iAngle = 360 / getCount(), angle = ZERO;
			for (int i = ZERO; i < getCount(); i++) {

				if (getCount() > ONE) {
					angle = (int) ((i + ONE) * iAngle - circlePoints[getCount() - ONE]);
					centerX = (int) ((right - left) / TWO + (getWidth() * mOriginDist)
							* Math.cos(Math.toRadians(angle)));
					centerY = (int) ((bottom - top) / TWO + (getWidth() * mOriginDist)
							* Math.sin(Math.toRadians(angle)));
				} else {
					centerX = right - left;
					centerY = bottom - top;
				}

				View v = getChildAt(i);
				Log.i("X/Y/angle/mOriginDist",
						centerX + "/" + centerY + "/" + angle + "/"
								+ mOriginDist + "/" + v.getMeasuredHeight());
				v.layout(centerX - v.getMeasuredWidth() / TWO,
						centerY - v.getMeasuredWidth() / TWO,
						centerX + v.getMeasuredWidth() / TWO,
						centerY + v.getMeasuredWidth() / TWO);
			}

			centerX = (right - left) / TWO;
			centerY = (bottom - top) / TWO;

			Log.i("X/Y2/angle/mOriginDist",
					centerX + "/" + centerY + "/" + angle + "/" + mOriginDist
							+ "/" + mCircleSelect.getMeasuredHeight());

			mCircleSelect.layout(
					centerX - mCircleSelect.getMeasuredWidth() / TWO, centerY
							- mCircleSelect.getMeasuredWidth() / TWO, centerX
							+ mCircleSelect.getMeasuredWidth() / TWO, centerY
							+ mCircleSelect.getMeasuredWidth() / TWO);

			setDragListener();
		}

	}

	public int getPoint(int[] lines, float[] point) {

		return getPointForLine(lines, point);
	}

	public int getPointForLine(int[] mOptionLineValues2, float[] pointA) {

		int x = ZERO, child = ZERO;
		float px1, py1, px2, py2;

		if (pointA[ONE] <= getHeight() / TWO) {

			child = 8;
			mCurrentChildLine = Line.TOP;

		} else {
			if (getChildCount() > THREE) {
				if (pointA[ZERO] <= getWidth() / TWO
						&& (mCurrentChildLine == Line.NONE || mCurrentChildLine == Line.TOP)) {

					mCurrentChildLine = Line.RIGHT;
					child = ZERO;
				} else {
					child = 4;
				}
			}

		}

		px1 = mOptionLineValues2[child++];
		py1 = mOptionLineValues2[child++];
		px2 = mOptionLineValues2[child++];
		py2 = mOptionLineValues2[child++];
		x = (int) (px1 + (pointA[ONE] - py1) * (px2 - px1) / (py2 - py1));
		return x;
	}

	public void setDragListener() {

		mCircleSelect.setOnTouchListener(new OnTouchListener() {

			@Override
			public boolean onTouch(View view, MotionEvent event) {

				int action = event.getAction();
				CircleView v = (CircleView) view;

				mCirclePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
				mCirclePaint.setColor(Color.BLACK);
				mCirclePaint.setStyle(Paint.Style.STROKE);

				int xOffset = v.getRight() - v.getLeft();
				int yOffset = v.getBottom() - v.getTop();

				switch (action) {

				case MotionEvent.ACTION_DOWN:
					mCircleSelect.setMoveFlag(true);
					Log.i("on", "down");

					if (mAnchorPosition == null) {
						mAnchorPosition = new int[4];
						mAnchorPosition[ZERO] = v.getLeft();
						mAnchorPosition[ONE] = v.getTop();
						mAnchorPosition[TWO] = v.getRight();
						mAnchorPosition[THREE] = v.getBottom();
					}
					v.invalidate();
					break;

				case MotionEvent.ACTION_MOVE:

					// int linePointX = getPointForLine(mOptionLineValues, new
					// float[] {event.getRawX(), event.getRawY() - 200});
					// v.layout(linePointX - xOffset/2, (int)event.getRawY() -
					// 200 - yOffset/2, linePointX + xOffset/2,(int)
					// event.getRawY() + yOffset/2 - 200);
					v.layout((int) event.getRawX() - xOffset / TWO,
							(int) event.getRawY() - 200 - yOffset / TWO,
							(int) event.getRawX() + xOffset / TWO,
							(int) event.getRawY() + yOffset / TWO - 200);

					Log.i("on", "move");
					break;

				case MotionEvent.ACTION_UP:
					v.setMoveFlag(false);
					Log.i("on", "up");
					mCurrentChildLine = Line.NONE;
					
					if (mOnHoverListener != null) {
						View hView = getHoveredItem(v);
						
						if (hView != null)
							mOnHoverListener.onHover(hView);
					}
					
					v.layout(mAnchorPosition[ZERO], mAnchorPosition[ONE],
							mAnchorPosition[TWO], mAnchorPosition[THREE]);
					v.invalidate();
				}
				return true;
			}
		});

		/*
		 * mCircleSelect.setOnDragListener(new OnDragListener() {
		 * 
		 * @Override public boolean onDrag(View v, DragEvent event) {
		 * 
		 * switch(event.getAction()) {
		 * 
		 * case DragEvent.ACTION_DRAG_ENTERED: Log.i("drag", "entered");
		 * Log.i("drag", event.getX() + "/" + event.getX()); break;
		 * 
		 * case DragEvent.ACTION_DRAG_STARTED: Log.i("drag", "started");
		 * Log.i("drag", event.getX() + "/" + event.getX()); break;
		 * 
		 * case DragEvent.ACTION_DRAG_LOCATION: Log.i("drag", event.getX() + "/"
		 * + event.getX()); break;
		 * 
		 * case DragEvent.ACTION_DROP: Log.i("drag", "drop"); Log.i("drag",
		 * event.getX() + "/" + event.getX()); break;
		 * 
		 * case DragEvent.ACTION_DRAG_EXITED: Log.i("drag", "exit");
		 * Log.i("drag", event.getX() + "/" + event.getX()); break;
		 * 
		 * case DragEvent.ACTION_DRAG_ENDED: Log.i("drag", "end"); Log.i("drag",
		 * event.getX() + "/" + event.getX()); break; } return false; } });
		 */
	}

	private View getHoveredItem(View view) {

		View childView;

		for (int i = ZERO; i < getChildCount() - ONE; i++) {

			childView = getChildAt(i);

			if (getDistance(childView, view) <= (view.getRight() - view
					.getLeft()) / TWO)
				return childView;
		}
		return null;
	}

	public int getDistance(View viewA, View viewB) {

		int radiusA = viewA.getWidth() / TWO, radiusB = viewB.getWidth() / TWO;
		int x1 = viewA.getLeft() + radiusA, y1 = viewA.getTop() + radiusA, x2 = viewB
				.getLeft() + radiusB, y2 = viewB.getTop() + radiusB;

		return (int) Math.sqrt(Math.pow((x2 - x1), TWO) + Math.pow((y2 - y1), TWO));
	}

	@Override
	protected void onSizeChanged(int w, int h, int oldw, int oldh) {
		super.onSizeChanged(w, h, oldw, oldh);

	}

	@Override
	public void onConfigurationChanged(Configuration newConfig) {
		super.onConfigurationChanged(newConfig);

		// Checks the orientation of the screen
		if (newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE) {
			mLayoutOrientation = Configuration.ORIENTATION_LANDSCAPE;
		} else if (newConfig.orientation == Configuration.ORIENTATION_PORTRAIT) {
			mLayoutOrientation = Configuration.ORIENTATION_PORTRAIT;
		}
	}

	private void init() {

		mLinePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
		mLinePaint.setColor(Color.DKGRAY);

		mCurrentChildLine = Line.NONE;
		setWillNotDraw(false);
	}

	@Override
	public Adapter getAdapter() {

		return mAdapter;
	}

	@Override
	public void setAdapter(Adapter adapter) {

		mAdapter = adapter;
		LayoutParams layoutParams;

		for (int i = ZERO; i < adapter.getCount(); i++) {

			View v = adapter.getView(i, null, this);
			layoutParams = v.getLayoutParams();

			if (layoutParams == null) {
				layoutParams = new LayoutParams(LayoutParams.WRAP_CONTENT,
						LayoutParams.WRAP_CONTENT);
			}

			addViewInLayout(v, i, layoutParams);
		}

		layoutParams = mCircleSelect.getLayoutParams();

		if (layoutParams == null) {
			layoutParams = new LayoutParams(LayoutParams.WRAP_CONTENT,
					LayoutParams.WRAP_CONTENT);
		}

		addViewInLayout(mCircleSelect, getCount(), layoutParams);

		Log.i("cnt", getCount() + "");

		makeLineData();

		invalidate();
		requestLayout();
	}

	private void makeLineData() {

		mOptionLineValues = new int[getCount() * 4];
	}

	@Override
	public View getSelectedView() {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public void setSelection(int position) {
		// TODO Auto-generated method stub

	}

}
