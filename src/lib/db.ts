import { PrismaClient } from "@prisma/client";

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

function buildPrisma(): PrismaClient {
  const url = process.env.DATABASE_URL ?? "file:./prisma/dev.db";

  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const { createClient } = require("@libsql/client");
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const { PrismaLibSql } = require("@prisma/adapter-libsql");
    const adapter = new PrismaLibSql({ url });
    return new PrismaClient({ adapter } as ConstructorParameters<typeof PrismaClient>[0]);
  } catch (e) {
    console.warn("Prisma adapter init failed, falling back:", e);
    return new PrismaClient();
  }
}

export const prisma: PrismaClient =
  globalForPrisma.prisma ?? buildPrisma();

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;
