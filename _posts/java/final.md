ok
```
class Point {
	public int x, y;
}
```


error
```
class Point {
	
	public final int x, y;

}
```

ok
```
class Point {
	
	public final int x, y;

	public Point(int x, int y) {
		this.x = x;
		this.y = y;
	}

}
```