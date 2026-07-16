# Demo Video Data

This script prepares a stable promo dataset for the product recording:

- Teacher account
- Two demo classes
- 24 demo students
- Tasks and task notifications
- System / health / review notifications
- Run-group activity content
- Activity history and statistics

## Run

From `backend/`:

```bash
python scripts/seed_demo_video.py --reset
```

Use `--reset` when you want to clear previous promo rows first.

## Recording Accounts

- Teacher: `18800000001` / `DemoTeacher123`
- Student A: `18800000101` / `DemoStudent123`
- Student B: `18800000102` / `DemoStudent123`

## Notes

- Demo rows are scoped with `[PROMO]`, `1880000...`, and `DEMO...`
- The script is safe for repeated runs on the same dev database
- It is intended for backend-generated demo content, not manual app input
