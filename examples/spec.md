# Example Refactoring Project

This is a template spec.md file. Replace this content with your specific refactoring instructions.

## Instructions

Describe WHAT to refactor and HOW to do it. The entire content of this file will be provided to Claude as context when working on each task.

### Guidelines

- Guideline 1: Be specific about patterns to follow
- Guideline 2: Include examples of before/after code
- Guideline 3: Document edge cases and exceptions
- Guideline 4: Reference existing code patterns to match

### Example

Before:
```javascript
// Old pattern
function getUserData(userId) {
  return db.query('SELECT * FROM users WHERE id = ' + userId);
}
```

After:
```javascript
// New pattern with parameterized query
function getUserData(userId) {
  return db.query('SELECT * FROM users WHERE id = ?', [userId]);
}
```

## Common Pitfalls

- Don't forget to update related tests
- Remember to handle error cases
- Maintain backwards compatibility where needed

## Checklist

Each unchecked item below will become a separate PR. Be specific!

- [ ] Refactor UserService to use parameterized queries
- [ ] Update AuthService database calls
- [ ] Convert ProductService to new pattern
- [ ] Migrate OrderService queries
- [x] Example completed task (this will be skipped)

## Notes

- You can add more context anywhere in this file
- Checklist items can be added at any point during the refactoring
- Completed items (- [x]) are automatically skipped
