<?php
namespace App\DBAL\Types;

use Doctrine\DBAL\Platforms\AbstractPlatform;
use Doctrine\DBAL\Types\Type;

class DirectionType extends Type
{
    public const DIRECTION_UP = '上り';
    public const DIRECTION_DOWN = '下り';

    public const POSSIBLE_VALUES = [
        self::DIRECTION_UP,
        self::DIRECTION_DOWN,
    ];

    const NAME = 'direction_enum';

    public function getSQLDeclaration(array $fieldDeclaration, AbstractPlatform $platform): string
    {
        return "ENUM('上り', '下り')";
    }

    public function convertToPHPValue($value, AbstractPlatform $platform): mixed
    {
        return $value;
    }

    public function convertToDatabaseValue($value, AbstractPlatform $platform): mixed
    {
        if (!in_array($value, self::POSSIBLE_VALUES, true)) {
            throw new \InvalidArgumentException("Invalid direction value");
        }

        return $value;
    }

    public function getName(): string
    {
        return self::NAME;
    }
}
