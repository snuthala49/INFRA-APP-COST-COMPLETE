import { NextResponse } from "next/server";

export async function POST() {
  return NextResponse.json({ error: "Contact email is disabled" }, { status: 404 });
}
