# Test Fixes

## Code Highlighting Test

```python
def hello_world():
    """This text should be readable on white background."""
    print("Hello, World!")
    return True
```

```javascript
// This should also be readable
function test() {
    const value = "readable text";
    return value;
}
```

## Mermaid Diagrams Test

### Flowchart
```mermaid
graph TD
    A[Flowchart] --> B[Should render]
    B --> C[In its own space]
```

### Class Diagram
```mermaid
classDiagram
    class Animal {
        +String name
        +makeSound()
    }
```

### State Diagram
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Running
    Running --> [*]
```

**All three diagrams above should be separate and not overlapping!**
