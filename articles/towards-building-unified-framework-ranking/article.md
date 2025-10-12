---
title: Towards building a unified framework for feature selection with ranking functions
date: Apr 7, 2021
description: One code to rule them all. One code to implement them all, and in the same framework bind them.
---

In the feature engineering of any data related project, we often have to filter the columns we will use to train our model manually; this filtering often relies on the insights we have on data and also on many criteria that can help us distinguish between the valuable attributes and the redundant or the meaningless ones, this process is known as the **feature selection**.

They are many different ways of selecting attributes; the one we see today is known as the ranking feature selection. It’s the most basic way. It evaluates each attribute with a function, ranks them and keeps the best attributes.

Although this ranking can be done with various methods, we will explore these method’s classification, see how this classification can help us organize them into a reliable and extensible framework, and use this framework to test and compare their behaviours.

## Feature selection ranking methods

In feature selection, we can classify the quality measure of an attribute into five categories according to the classification made by Dash and Liu.

- Distance measures: These quantify the correlation between the attributes and the label.
- Information measures: These information theory measures are interested in the label’s entropy after splitting them according to a feature's value.
- Consistency measures: A feature is consistent if the same values are not associated with different values of the class.
- Dependency measures: Two variables are said to be independent if the probability of taking a specific value is not influenced by information on the other's value, so these measures work by quantifying the class's dependency on an attribute.
- Classification measures: These measures are time expensive; they evaluate the classification quality when taking a specific attribute.

I will, of course, come back to each of these classes when presenting the measures I will consider.
