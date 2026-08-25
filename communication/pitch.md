# databricks-twin — elevator pitch

> Written to be said out loud, not read. Two lengths below — use the short one
> if you only get a few sentences, the fuller one if they ask "tell me more."
> No video for this one, on purpose — this is meant to stay light.

## 30 seconds

After we talked about openrag-twin, I wanted to show that wasn't a one-stack fluke — so I
built the same kind of routing agent again, from scratch, on Databricks: real workspace,
Unity Catalog, Vector Search, Genie, the works. Same two-tool decision problem — search docs
versus look up structured data — but this time the second tool is a Genie space doing real
natural-language-to-SQL instead of a mock I wrote myself. It's deployed, it's measured — 82%
on a golden set I built the same way as before — and I found and fixed four real bugs along
the way, including one that only showed up once I actually deployed it to production.

## Fuller version (~90 seconds)

You gave me great feedback on openrag-twin, and the thing I wanted to prove next wasn't "I
can build another RAG demo" — it was that the way I work holds up on a completely different
stack, not just the one I happened to pick first.

So I took the same core idea — an agent that has to *decide* which tool to use, not just
retrieve and hope — and rebuilt it on Databricks. Same shape of problem: a question about
documentation should search a real doc corpus and cite its source; a question about a support
ticket should skip the docs entirely. But instead of porting my ticket-lookup mock over, I
used something genuinely Databricks-native for it: a Genie space, which does
natural-language-to-SQL against a governed Unity Catalog table. The agent doesn't write SQL —
it asks Genie a question in English, and Genie generates and runs the query.

I ran it on a real workspace, not a sandbox — Free Edition, so it cost nothing — and I
deployed it as an actual Databricks App, not just localhost. Same standard as before: I
measured it with a golden set rather than eyeballing it — 82% on the routing checks, run
three times so it's a real number and not a lucky pass — and I documented four real bugs
instead of hiding them. The interesting one only showed up once I deployed to production: it
worked locally under my own account, then failed live with a permissions error, because
Databricks Genie runs its generated SQL under the caller's own rights, not just the app's
access to the Genie space itself. Found it, understood why, fixed it, and wrote it down.

That's really the point of this one: same rigor, different vendor, and proof I actually go
looking for what breaks instead of stopping once the demo works once.
