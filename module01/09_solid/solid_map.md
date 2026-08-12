# SOLID map

| | **Principle** | In one sentence | The smell that means you broke it | Where it lives here |
| --- | ------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------ | ---------------------------- |
| **S** | Single Responsibility | One module, one reason to change | You cannot reuse a part without copying the whole | `s_single_responsibility/` |
| **O** | Open/Closed               | Add behaviour by adding code, not by editing working code    | Every new feature edits the same `if/elif`                     | `o_open_closed/`             |
| **L** | Liskov Substitution       | A subtype must keep every promise its base type makes        | A subclass raises where the base does not, or ignores an override | `l_liskov/`               |
| **I** | Interface Segregation     | No client depends on methods it does not call                | Implementations full of `NotImplementedError` stubs            | `i_interface_segregation/`   |
| **D** | Dependency Inversion      | Policy and detail both depend on an abstraction              | A class builds its own collaborators in `__init__`             | `d_dependency_inversion/`    |

"One reason to change" is about *who asks*. Four teams that all have to edit one function is an SRP
problem even if that function is beautifully written.

## The one-line test for each

| Principle | Ask yourself |
| --- | --- |
| **S** | Can I get the total without also printing the report? |
| **O** | To add the next one of these, how many existing files do I edit? |
| **L** | Can I hand this subclass to code written for the base class and walk away? |
| **I** | How many methods does the smallest useful test double need? |
| **D** | Can I construct this class with the network unplugged? |

## `typing.Protocol` versus `abc.ABC`

| | **`typing.Protocol`** | **`abc.ABC`** |
| ---------------------------- | ---------------------------------------- | ---------------------------------------- |
| **An implementer must**      | match the shape                          | inherit explicitly                        |
| **Third-party classes**      | work as-is                               | need `register()` or a wrapper            |
| **When it is checked**       | statically, at every call site           | at runtime, on instantiation              |
| **Can carry shared code**    | no (only defaults on the protocol)       | yes — concrete methods on the base        |
| **`isinstance()`**           | only with `@runtime_checkable`, and it checks method *names* only | always, and it is exact |
| **Who declares the relationship** | the consumer                        | the implementer                           |
| **Reach for it when**        | "anything that quacks like this" — especially code you do not own | a family you own that shares behaviour |

The examples in this folder use ABCs throughout, so the interfaces are visible as classes on screen —
`i_interface_segregation/after.py` composes three role interfaces by multiple inheritance, and
`d_dependency_inversion/after.py` injects a `Notifier` ABC. Every one of them would work identically as
a `Protocol`; the table above is the trade-off you would be making.

A note on `@runtime_checkable`: `isinstance(obj, SomeProtocol)` verifies that the method *names* exist.
It does not check signatures, argument types or return types. An object whose `close` attribute is the
integer 7 passes. Use it as a smoke test, never as proof.

## L and I are usually the same conversation

The classic Liskov violation — a subclass that raises `NotImplementedError` from a method its base type
promises — is almost always caused by an interface that was too wide to begin with. The subclass had no
honest way to implement it, so it lied.

Interface Segregation is the fix: split the interface until every implementer can back every claim it
makes. `l_liskov/before.py` shows the violation with a read-only storage that refuses `save()`;
`l_liskov/after.py` and `i_interface_segregation/after.py` both show the cure.

The old `../solid/I/01.py` in this repository is exactly this: a `ReadOnlyStorage` raising
`NotImplementedError` from `upload()`, filed under the letter I. The defect is L; the remedy is I. Both
letters, one file, by accident.

## SOLID and design patterns

SOLID states the goals. Patterns are named ways of reaching them.

| Goal (SOLID) | Some means (patterns) |
| --- | --- |
| Open/Closed | Strategy, Registry, plugin entry points, Chain of Responsibility |
| Dependency Inversion | constructor injection, `Protocol`, FastAPI's `Depends`, a DI container |
| Single Responsibility | Repository, Adapter, Template Method's hook split |
| Interface Segregation | role interfaces, Adapter |
| Liskov | contract tests, composition instead of inheritance |

Learn the goals. The patterns are vocabulary for describing which means you used — which is worth having,
but it is the second thing, not the first.

One connection worth pointing at in the lecture: `o_open_closed/after.py` **is** Strategy —
interchangeable `Discount` objects behind one interface, as in
[`../08_patterns/05_strategy.py`](../08_patterns/05_strategy.py). The pattern is the mechanism;
Open/Closed is the goal it serves.
