Hystrix熔断器源码分析.md


```
static final ConcurrentMap<String, HealthCountsStream> streams = new ConcurrentHashMap<String, HealthCountsStream>();

private static final int NUM_EVENT_TYPES = HystrixEventType.values().length;

public static HealthCountsStream getInstance(HystrixCommandKey commandKey, int numBuckets, int bucketSizeInMs) {
    HealthCountsStream initialStream = streams.get(commandKey.name());
    if (initialStream != null) {
        return initialStream;
    } else {
        synchronized (HealthCountsStream.class) {
            HealthCountsStream existingStream = streams.get(commandKey.name());
            if (existingStream == null) {
                HealthCountsStream newStream = new HealthCountsStream(commandKey, numBuckets, bucketSizeInMs,
                        HystrixCommandMetrics.appendEventToBucket);
                newStream.startCachingStreamValuesIfUnstarted();
                streams.putIfAbsent(commandKey.name(), newStream);
                return newStream;
            } else {
                return existingStream;
            }
        }
    }
}

@Override
long[] getEmptyBucketSummary() {
    return new long[NUM_EVENT_TYPES];
}
```


```
static class HystrixCircuitBreakerImpl implements HystrixCircuitBreaker {
        private final HystrixCommandProperties properties;
        private final HystrixCommandMetrics metrics;

        /* track whether this circuit is open/closed at any given point in time (default to false==closed) */
        private AtomicBoolean circuitOpen = new AtomicBoolean(false);

        /* when the circuit was marked open or was last allowed to try a 'singleTest' */
        private AtomicLong circuitOpenedOrLastTestedTime = new AtomicLong();

        protected HystrixCircuitBreakerImpl(HystrixCommandKey key, HystrixCommandGroupKey commandGroup, HystrixCommandProperties properties, HystrixCommandMetrics metrics) {
            this.properties = properties;
            this.metrics = metrics;
        }

        public void markSuccess() {
            if (circuitOpen.get()) {
                if (circuitOpen.compareAndSet(true, false)) {
                    //win the thread race to reset metrics
                    //Unsubscribe from the current stream to reset the health counts stream.  This only affects the health counts view,
                    //and all other metric consumers are unaffected by the reset
                    metrics.resetStream();
                }
            }
        }

        @Override
        public boolean allowRequest() {
            if (properties.circuitBreakerForceOpen().get()) {
                // properties have asked us to force the circuit open so we will allow NO requests
                return false;
            }
            if (properties.circuitBreakerForceClosed().get()) {
                // we still want to allow isOpen() to perform it's calculations so we simulate normal behavior
                isOpen();
                // properties have asked us to ignore errors so we will ignore the results of isOpen and just allow all traffic through
                return true;
            }
            return !isOpen() || allowSingleTest();
        }

        public boolean allowSingleTest() {
            long timeCircuitOpenedOrWasLastTested = circuitOpenedOrLastTestedTime.get();
            // 1) if the circuit is open
            // 2) and it's been longer than 'sleepWindow' since we opened the circuit
            if (circuitOpen.get() && System.currentTimeMillis() > timeCircuitOpenedOrWasLastTested + properties.circuitBreakerSleepWindowInMilliseconds().get()) {
                // We push the 'circuitOpenedTime' ahead by 'sleepWindow' since we have allowed one request to try.
                // If it succeeds the circuit will be closed, otherwise another singleTest will be allowed at the end of the 'sleepWindow'.
                if (circuitOpenedOrLastTestedTime.compareAndSet(timeCircuitOpenedOrWasLastTested, System.currentTimeMillis())) {
                    // if this returns true that means we set the time so we'll return true to allow the singleTest
                    // if it returned false it means another thread raced us and allowed the singleTest before we did
                    return true;
                }
            }
            return false;
        }

        @Override
        public boolean isOpen() {
            if (circuitOpen.get()) {
                // if we're open we immediately return true and don't bother attempting to 'close' ourself as that is left to allowSingleTest and a subsequent successful test to close
                return true;
            }

            // we're closed, so let's see if errors have made us so we should trip the circuit open
            HealthCounts health = metrics.getHealthCounts();

            // check if we are past the statisticalWindowVolumeThreshold
            if (health.getTotalRequests() < properties.circuitBreakerRequestVolumeThreshold().get()) {
                // we are not past the minimum volume threshold for the statisticalWindow so we'll return false immediately and not calculate anything
                return false;
            }

            if (health.getErrorPercentage() < properties.circuitBreakerErrorThresholdPercentage().get()) {
                return false;
            } else {
                // our failure rate is too high, trip the circuit
                if (circuitOpen.compareAndSet(false, true)) {
                    // if the previousValue was false then we want to set the currentTime
                    circuitOpenedOrLastTestedTime.set(System.currentTimeMillis());
                    return true;
                } else {
                    // How could previousValue be true? If another thread was going through this code at the same time a race-condition could have
                    // caused another thread to set it to true already even though we were in the process of doing the same
                    // In this case, we know the circuit is open, so let the other thread set the currentTime and report back that the circuit is open
                    return true;
                }
            }
        }

    }
```