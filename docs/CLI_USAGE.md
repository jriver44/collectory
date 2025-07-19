# CLI Usage

After installation, you’ll have the `curation` command:

```bash
curation my_collection
```

Sample session:

```
Please enter name of desired collection file to load
→ my_collection
1) Add Item
2) Remove Item
3) Edit Category
4) View Items
5) Save Collection
6) Summary
7) Filter by Category
8) Search by Keyword
9) Quit

> 1
Enter item name: Padron 1964
Enter category: Cigar
Quantity to add: 1
✔ Created new item 'Padron 1964' x 1

> 4
┌────┬───────────────┬─────────┬──────────┬────────────────────┐
│ ID │ Name          │ Category│ Quantity │ Time               │
├────┼───────────────┼─────────┼──────────┼────────────────────┤
│ 1  │ Padron 1964   │ Cigar   │ 1        │ 2025-07-04 10:00:00│
└────┴───────────────┴─────────┴──────────┴────────────────────┘

> 9
Saving before exit...
✔ Final save succeeded.
```