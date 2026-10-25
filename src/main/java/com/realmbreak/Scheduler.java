package com.realmbreak;

import java.util.ArrayList;
import java.util.List;

/** Tiny server-tick scheduler. */
public final class Scheduler {
    private static final class Task {
        int left;
        final Runnable run;
        Task(int left, Runnable run) {
            this.left = left;
            this.run = run;
        }
    }

    private static final List<Task> TASKS = new ArrayList<>();

    private Scheduler() {}

    public static void after(int ticks, Runnable r) {
        synchronized (TASKS) {
            TASKS.add(new Task(Math.max(1, ticks), r));
        }
    }

    public static void tick() {
        List<Runnable> due = null;
        synchronized (TASKS) {
            if (TASKS.isEmpty()) return;
            for (int i = TASKS.size() - 1; i >= 0; i--) {
                Task t = TASKS.get(i);
                if (--t.left <= 0) {
                    if (due == null) due = new ArrayList<>();
                    due.add(0, t.run);
                    TASKS.remove(i);
                }
            }
        }
        if (due != null) {
            for (Runnable r : due) {
                try {
                    r.run();
                } catch (Exception ex) {
                    Realmbreak.LOGGER.error("Scheduled task failed", ex);
                }
            }
        }
    }

    public static void clear() {
        synchronized (TASKS) {
            TASKS.clear();
        }
    }
}
