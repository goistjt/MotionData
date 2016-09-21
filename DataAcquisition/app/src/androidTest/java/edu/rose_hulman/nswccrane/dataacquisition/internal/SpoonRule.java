/*
 * Copyright (C) 2015 Jake Wharton
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package edu.rose_hulman.nswccrane.dataacquisition.internal;

import android.app.Activity;

import com.squareup.spoon.Spoon;

import org.junit.rules.TestWatcher;
import org.junit.runner.Description;

public class SpoonRule extends TestWatcher {

    private String className;
    private String methodName;

    @Override
    protected void starting(Description description) {
        super.starting(description);
        className = description.getClassName();
        methodName = description.getMethodName();
    }

    public void takeScreenshot(Activity activity, String tag) {
        Spoon.screenshot(activity, tag, className, methodName);
    }

}
