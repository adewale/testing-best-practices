Yes. Because Email has unexported fields, invalid Email values are unconstructible. You can confirm `Email{}` outside the package compiles, and then delete all invalid-email tests downstream.
