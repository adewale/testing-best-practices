// A small order service. Two operations with primitive-typed parameters and
// heavy runtime validation that could be lifted into the type system (branded
// types, Zod schemas, or smart constructors).

export interface Order {
  customerId: string;
  items: string[];
  totalCents: number;
  createdAt: Date;
}

export function createOrder(
  customerId: string,
  items: string[],
  totalCents: number,
): Order {
  if (!customerId || customerId.length === 0) {
    throw new Error("customerId required");
  }
  if (customerId.length > 32) {
    throw new Error("customerId too long");
  }
  if (!/^[a-zA-Z0-9_-]+$/.test(customerId)) {
    throw new Error("customerId has invalid characters");
  }
  if (!items || items.length === 0) {
    throw new Error("at least one item required");
  }
  for (const item of items) {
    if (!item || item.length === 0) {
      throw new Error("empty item not allowed");
    }
  }
  if (!Number.isInteger(totalCents) || totalCents < 0) {
    throw new Error("totalCents must be non-negative integer");
  }
  if (totalCents > 100_000_000) {
    throw new Error("totalCents exceeds max");
  }
  return { customerId, items, totalCents, createdAt: new Date() };
}

export function applyDiscount(
  order: Order,
  discountCents: number,
): Order {
  if (!order || typeof order.totalCents !== "number") {
    throw new Error("invalid order");
  }
  if (!Number.isInteger(discountCents) || discountCents < 0) {
    throw new Error("discount must be non-negative integer");
  }
  if (discountCents > order.totalCents) {
    throw new Error("discount exceeds total");
  }
  return { ...order, totalCents: order.totalCents - discountCents };
}

export function isHighValue(order: Order): boolean {
  // Yet another consumer that re-checks the shape and value.
  if (!order || typeof order.totalCents !== "number" || order.totalCents < 0) {
    return false;
  }
  return order.totalCents >= 10_000;
}
