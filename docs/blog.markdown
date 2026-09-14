---
layout: page
title: Blog
description: Announcements from the DMI project.
permalink: /blog/
---

{%- if site.posts.size > 0 -%}
<ul class="post-list">
  {%- for post in site.posts -%}
  <li>
    <span class="post-meta">{{ post.date | date: "%-d %b %Y" }}</span>
    <h3><a class="post-link" href="{{ post.url | relative_url }}">{{ post.title | escape }}</a></h3>
    {%- if site.show_excerpts -%}
      {{ post.excerpt }}
    {%- endif -%}
  </li>
  {%- endfor -%}
</ul>

<p class="rss-subscribe">subscribe <a href="{{ "/feed.xml" | relative_url }}">via RSS</a></p>
{%- else -%}
<p>No posts yet.</p>
{%- endif -%}
