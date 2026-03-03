# Monaco Debug Guide for HackerRank

## Quick Debug Steps

### 1. Check if Monaco is detected
Open HackerRank problem → Press F12 → Console → Type:

```javascript
typeof monaco
```

Expected: `"object"` or `"undefined"`

### 2. Check Monaco editors
```javascript
monaco.editor.getEditors()
```

Expected: Array with 1 or more editors

### 3. Check if our fix is loaded
```javascript
// In console, after pressing Ctrl+Alt+A
// Look for these messages:
// [CodeTyper] Monaco content set successfully
// OR
// [CodeTyper] Monaco direct insert failed: ...
```

### 4. Manual Monaco Test
```javascript
// Get the editor
const editor = monaco.editor.getEditors()[0];
const model = editor.getModel();

// Try inserting text
const pos = model.getFullModelRange().getEndPosition();
const range = new monaco.Range(pos.lineNumber, pos.column, pos.lineNumber, pos.column);
model.pushEditOperations([], [{ range: range, text: 'test' }], () => null);
```

If this works manually, the problem is in our extension code.
If this fails, Monaco has a different API on HackerRank.

## Common Issues

### Issue 1: Bridge not working
Check console for:
- `[Bridge] Bridge ready`
- `[CodeTyper] Bridge ready, editor: monaco`

### Issue 2: Direct fallback failing
If you see `Monaco direct insert failed:`, the detection is working but the API call is wrong.

### Issue 3: execCommand still being used
If you DON'T see "Monaco content set successfully", the execCommand path is being used.

## Next Steps

1. Share console output after pressing Ctrl+Alt+A
2. Share result of `typeof monaco` in console
3. Share any errors that appear

